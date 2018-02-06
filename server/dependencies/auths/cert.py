#!/usr/bin/env python

import M2Crypto as m2
import OpenSSL as ssl
import ctypes
import datetime
import getpass
import hashlib
import os

from pyspkac import SPKAC


MBSTRING_FLAG = 0x1000
MBSTRING_ASC = MBSTRING_FLAG | 1


# for more on objectIds see: https://tools.ietf.org/html/rfc3279#section-2.2.1
# https://tools.ietf.org/html/rfc4055#section-2.1
def gen_key_csr(name, mail, org=None, klen=4096, pext=0x10001):
    """ creates a 4K RSA key and a related CSR based on the parameters
    """
    sec, pub = gen_key(klen, pext)
    csr = gen_csr(sec, name, mail, org)
    return (sec, pub, csr)


def gen_key(klen=4096, pext=0x10001):
    """ generates a 4K RSA key in PEM format
    """
    keypair = m2.RSA.gen_key(klen, pext)

    pkey = m2.EVP.PKey(md='sha512')
    pkey.assign_rsa(keypair)
    return (keypair.as_pem(cipher=None),
            m2.RSA.new_pub_key(keypair.pub()).as_pem(cipher=None))


def gen_csr(key, name=None, email=None, org=None):
    """ generates a CSR using the supplied parameters
    """
    key = load_key(key)

    # create csr
    csr = m2.X509.Request()
    dn = m2.X509.X509_Name()
    if org:
        dn.add_entry_by_txt(field='O', type=MBSTRING_ASC,
                            entry=org, len=-1, loc=-1, set=0)
    if name:
        dn.add_entry_by_txt(field='CN', type=MBSTRING_ASC,
                            entry=name, len=-1, loc=-1, set=0)
    if email:
        dn.add_entry_by_txt(
            field='emailAddress', type=MBSTRING_ASC,
            entry=email, len=-1, loc=-1, set=0)
    csr.set_subject_name(dn)
    csr.set_pubkey(pkey=key)
    csr.sign(pkey=key, md='sha512')
    return csr.as_pem()


def pkcs12(key, cert, root_cert):
    """ creates a PKCS12 certificate for based on the supplied parameters
    """
    p12 = ssl.crypto.PKCS12()
    p12.set_privatekey(ssl.crypto.load_privatekey(ssl.SSL.FILETYPE_PEM, key))
    p12.set_certificate(ssl.crypto.load_certificate(
        ssl.SSL.FILETYPE_PEM, cert))
    p12.set_ca_certificates(
        (ssl.crypto.load_certificate(ssl.SSL.FILETYPE_PEM, root_cert),))
    return p12.export(getpass.getpass("Password for importing this key: "))


def spkac2pem(pk):
    csr = m2.X509.Request()
    csr.set_subject_name(pk.subject)
    csr.set_pubkey(pk.pkey)
    return csr.as_pem()


def spkac2cert(pk, email, name=None):
    pk = SPKAC(pk)
    csr = m2.X509.Request()
    csr.set_subject_name(pk.subject)
    csr.set_pubkey(pk.pkey)
    dn = csr.get_subject()

    print(dn, len(dn), type(dn))

    if len(dn) == 0:
        dn = m2.X509.X509_Name()
        if name:
            dn.add_entry_by_txt(field='CN', type=MBSTRING_ASC,
                                entry=name, len=-1, loc=-1, set=0)
        dn.add_entry_by_txt(
            field='emailAddress', type=MBSTRING_ASC,
            entry=email, len=-1, loc=-1, set=0)
        csr.set_subject_name(dn)
    return csr.as_pem()


def todn(obj):
    """ converts the DN to a dictionary
    """
    dn = str(obj)
    return dict(
        [(ass.split('=')[0], '='.join(
            ass.split('=')[1:])) for ass in dn.split('/') if ass])


def load_key(txt):
    """ loads an RSA key from a PEM string
    """
    bio = m2.BIO.MemoryBuffer(txt)
    keypair = m2.RSA.load_key_bio(bio)
    key = m2.EVP.PKey(md='sha512')
    key.assign_rsa(keypair)
    return key


def load(path):
    """ loads a file from disk to memory
    """
    raw_file = open(path, 'r')
    contents = raw_file.read()

    raw_file.close()

    return contents


class CertififcateAuthority(object):
    """represents a CA
    """
    # def __init__(self, pub, sec, serial, crl, incoming):

    def __init__(self, path):
        """Initializes the CA
        """
        self.path = path
        with open(path + '/ca.cfg', 'r') as fd:
            cfg = dict([[x.strip() for x in line.split('=')]
                        for line in fd.readlines()])

        self._pub = load(path + '/' + cfg['pub']
                         if cfg['pub'][0] != '/' else cfg['pub'])
        self._sec = load(path + '/' + cfg['sec']
                         if cfg['sec'][0] != '/' else cfg['sec'])
        self._serial = int(
            load(path + '/' + cfg['serial']
                 if cfg['serial'][0] != '/' else cfg['serial']))
        self._serialfname = ((
            path + '/' + cfg['serial'])
            if cfg['serial'][0] != '/' else cfg['serial'])
        self._crl = cfg['crl']
        self._incoming = ((
            path + '/' + cfg['incoming'])
            if cfg['incoming'][0] != '/' else cfg['incoming'])

        # calculate dn
        bio = m2.BIO.MemoryBuffer(self._pub)
        self.cert = m2.X509.load_cert_bio(bio)
        self.dn = todn(self.cert.get_issuer())

    def serial(self):
        """ increments persistently and returns the serial counter
        """
        self._serial += 1
        # TODO implement locking!!!
        with open(self._serialfname, 'w') as fd:
            fd.write("%02d" % self._serial)
        return self._serial

    def gen_cert(self, name, mail, org=None, klen=4096, pext=0x10001):
        """ automagically creates an untrusted PKCS12 certthe correct way, then
            use genkeycsr and a manual procedure.
        """
        sec, pub = gen_key(klen, pext)
        csr = gen_csr(sec, name, mail, org)
        cert = self.sign_csr(csr)
        return pkcs12(sec, cert, self._pub)

    def sign_csr(self, csr, valid=1):
        """ returns a PEM that contains a signed CSR with a validity
            specified in years
        """
        casec = load_key(self._sec)
        if type(csr) in [str, unicode]:
            bio = m2.BIO.MemoryBuffer(csr)
            csr = m2.X509.load_request_bio(bio)
        cert = m2.X509.X509()
        cert.set_version(2)
        # time notBefore
        ASN1 = m2.ASN1.ASN1_UTCTIME()
        ASN1.set_datetime(datetime.datetime.now())
        cert.set_not_before(ASN1)
        # time notAfter
        ASN1 = m2.ASN1.ASN1_UTCTIME()
        ASN1.set_datetime(datetime.datetime.now() +
                          datetime.timedelta(days=int(365 * valid)))
        cert.set_not_after(ASN1)
        # public key
        cert.set_pubkey(pkey=csr.get_pubkey())
        # subject
        cert.set_subject_name(csr.get_subject())
        # issuer
        dn = m2.X509.X509_Name(m2.m2.x509_name_new())

        if self.dn.get('C'):
            dn.add_entry_by_txt(field='C', type=MBSTRING_ASC,
                                entry=self.dn['C'], len=-1, loc=-1, set=0)
        if self.dn.get('O'):
            dn.add_entry_by_txt(field='O', type=MBSTRING_ASC,
                                entry=self.dn['O'], len=-1, loc=-1, set=0)
        dn.add_entry_by_txt(field='CN', type=MBSTRING_ASC,
                            entry=self.dn['CN'], len=-1, loc=-1, set=0)

        dn.add_entry_by_txt(field='emailAddress', type=MBSTRING_ASC,
                            entry=self.dn['emailAddress'], len=-1,
                            loc=-1, set=0)

        cert.set_issuer_name(dn)

        # Set the X509 extenstions
        # cert.add_ext(m2.X509.new_extension('nsCertType', 'client'))
        # cert.add_ext(m2.X509.new_extension('extendedKeyUsage', 'clientAuth',
        #                                critical=1))
        # cert.add_ext(m2.X509.new_extension('keyUsage', 'digitalSignature',
        #                                critical=1))
        cert.add_ext(m2.X509.new_extension('basicConstraints', 'CA:FALSE'))

        # Create the subject key identifier
        modulus = cert.get_pubkey().get_modulus()
        sha_hash = hashlib.sha1(modulus).digest()
        sub_key_id = ":".join(["%02X" % ord(byte) for byte in sha_hash])
        cert.add_ext(m2.X509.new_extension('subjectKeyIdentifier', sub_key_id))

        # Authority Identifier
        bio = m2.BIO.MemoryBuffer(self._pub)
        dummy = m2.X509.load_cert_bio(bio)
        cert.add_ext(dummy.get_ext('authorityKeyIdentifier'))

        cert.add_ext(m2.X509.new_extension('nsCaRevocationUrl', self._crl))

        # load serial number
        cert.set_serial_number(self.serial())

        # signing
        cert.sign(pkey=casec, md='sha512')
        # print cert.as_text()
        return cert.as_pem()

    def submit(self, csr):
        """ stores an incoming CSR for later certification
        """
        bio = m2.BIO.MemoryBuffer(csr)
        csr = m2.X509.load_request_bio(bio)
        modulus = csr.get_pubkey().get_modulus()
        hashsum = hashlib.sha1(modulus).hexdigest()
        with open(self._incoming + '/' + hashsum, 'a') as fd:
            fd.write(csr.as_pem())

    def incoming(self):
        """ returns a list of req objects to be certified
        """
        res = []
        for fname in sorted(os.listdir(self._incoming)):
            if fname.endswith('.invalid'):
                continue
            bio = m2.BIO.MemoryBuffer(load(self._incoming + '/' + fname))
            try:
                csr = m2.X509.load_request_bio(bio)
            except ValueError:
                print(self._incoming + '/' + fname, "is fishy, skipping")
                continue
            res.append((csr, self._incoming + '/' + fname))
        return res

    def signincoming(self, scrutinizer=None):
        """ signs all incoming CSRs before doing so it consults the
            optional scrutinizer for approval.
        """
        signed = []
        for csr, path in self.incoming():
            if not scrutinizer or scrutinizer(csr):
                cert = self.signcsr(csr)
                print("signed", csr.get_subject())
                if cert:
                    os.unlink(path)
                    signed.append(cert)
            else:
                os.rename(path, path + '.invalid')
        return signed

    @classmethod
    def create_ca(self, path, crl, name, mail,
                  org=None, valid=5, parentCA=None):
        """ creates and initializes a new CA on the filesystem
        """
        if not os.path.exists(path):
            os.mkdir(path)
        for d in ['conf', 'certs', 'public', 'private', 'incoming']:
            os.mkdir(path + '/' + d)

        os.chmod(path + "/private", '0700')

        # initialize serial
        with open(path + '/conf/serial', 'w') as fd:
            fd.write("01")

        sec, pub = gen_key()
        with open(path + '/private/root.pem', 'w') as fd:
            fd.write(sec)

        sec = load_key(sec)

        # create csr
        cert = m2.X509.X509()
        cert.set_version(2)
        cert.set_pubkey(pkey=sec)

        dn = m2.X509.X509_Name()
        if org:
            dn.add_entry_by_txt(field='O', type=MBSTRING_ASC,
                                entry=org, len=-1, loc=-1, set=0)
        dn.add_entry_by_txt(field='CN', type=MBSTRING_ASC,
                            entry=name, len=-1, loc=-1, set=0)
        dn.add_entry_by_txt(
            field='emailAddress', type=MBSTRING_ASC,
            entry=mail, len=-1, loc=-1, set=0)
        cert.set_subject_name(dn)
        if parentCA:
            cert.set_issuer_name(parentCA.cert.get_issuer())
        else:
            cert.set_issuer_name(dn)

        # serial 8 byte random
        serial = int(ssl.rand.bytes(8).encode('hex'), 16)
        cert.set_serial_number(serial)

        # time notBefore - from original PGP key
        ASN1 = m2.ASN1.ASN1_UTCTIME()
        now = datetime.datetime.now()
        ASN1.set_datetime(now)
        cert.set_not_before(ASN1)
        # time notAfter - from original PGP key
        ASN1 = m2.ASN1.ASN1_UTCTIME()
        ASN1.set_datetime(now + datetime.timedelta(days=int(365 * valid)))
        cert.set_not_after(ASN1)

        # Set the X509 extenstions
        cert.add_ext(m2.X509.new_extension('basicConstraints', 'CA:TRUE'))
        if parentCA:
            cert.add_ext(m2.X509.new_extension(
                'keyUsage', 'critical, keyCertSign'))

        # Create the subject key identifier
        modulus_str = cert.get_pubkey().get_modulus()
        sha_hash = hashlib.sha1(modulus_str).digest()
        sub_key_id = ":".join(["%02X" % ord(byte) for byte in sha_hash])
        cert.add_ext(new_extension('subjectKeyIdentifier', sub_key_id))

        # Authority Identifier
        if parentCA:
            cert.add_ext(parentCA.cert.get_ext('authorityKeyIdentifier'))
        else:
            authid = 'keyid,issuer:always'
            cert.add_ext(new_extension(
                'authorityKeyIdentifier', authid, issuer=cert))

        cert.add_ext(m2.X509.new_extension('nsCaRevocationUrl', crl))

        if parentCA:
            cert.sign(pkey=load_key(parentCA._sec), md='sha512')
        else:
            # self sign
            cert.sign(pkey=sec, md='sha512')

        with open(path + '/public/root.pem', 'w') as fd:
            fd.write(cert.as_pem())

        # dump initial config
        with open(path + '/ca.cfg', 'w') as fd:
            fd.write("crl=%s\nsec=%s\npub=%s\nserial=%s\nincoming=%s" % (
                crl,
                os.path.abspath(path + "/private/root.pem"),
                os.path.abspath(path + "/public/root.pem"),
                os.path.abspath(path + "/conf/serial"),
                os.path.abspath(path + "/incoming")))

        return CertififcateAuthority(path)


class Ctx(ctypes.Structure):
    _fields_ = [('flags', ctypes.c_int),
                ('issuer_cert', ctypes.c_void_p),
                ('subject_cert', ctypes.c_void_p),
                ('subject_req', ctypes.c_void_p),
                ('crl', ctypes.c_void_p),
                ('db_meth', ctypes.c_void_p),
                ('db', ctypes.c_void_p),
                ]


def fix_ctx(m2_ctx, issuer=None):
    ctx = Ctx.from_address(int(m2_ctx))

    ctx.flags = 0
    ctx.subject_cert = None
    ctx.subject_req = None
    ctx.crl = None
    if issuer is None:
        ctx.issuer_cert = None
    else:
        ctx.issuer_cert = int(issuer.x509)


def new_extension(name, value, critical=0, issuer=None, _pyfree=1):
    """
    Create new X509_Extension instance.
    """
    if name == 'subjectKeyIdentifier' and \
            value.strip('0123456789abcdefABCDEF:') is not '':
        raise ValueError('value must be precomputed hash')

    lhash = m2.m2.x509v3_lhash()
    ctx = m2.m2.x509v3_set_conf_lhash(lhash)
    # ctx not zeroed
    fix_ctx(ctx, issuer)

    x509_ext_ptr = m2.m2.x509v3_ext_conf(lhash, ctx, name, value)
    # ctx,lhash freed

    if x509_ext_ptr is None:
        raise Exception
    x509_ext = m2.X509.X509_Extension(x509_ext_ptr, _pyfree)
    x509_ext.set_critical(critical)
    return x509_ext
