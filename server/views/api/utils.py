import arrow

from datetime import date


def clean(collection):
    del collection['_id']

    return collection


def _search(bvn, app):
    bio = app.db.bios.find_one(
        {'_id': bvn}, projection=['bvn', 'first_name', 'last_name',
                                  'gender', 'dob', 'created_at'])

    if not bio:
        bio = {'status': 'error', 'data': None,
               'message': 'Unknown Bank Verification Number'}

    bio['dob'] = get_age(bio.get('dob'))
    bio['created_at'] = humanize_date(bio.get('created_at'))

    payrolls = app.db.payrolls.find({'_id': bvn})
    work = app.db.work_histories.find({'_id': bvn})
    data = {}
    data['payrolls'] = payrolls.distinct('rows')
    data['work_histories'] = work.distinct('rows')
    data['mortgages'] = []
    data['rents'] = []
    data['utilities'] = []
    data['loans'] = []

    bio.update(buckets=data)

    return bio


def get_age(born=None):

    if not born:
        return 'No Age Record'
    born = arrow.get(born).datetime
    today = date.today()
    age = today.year - born.year - (
        (today.month, today.day) < (born.month, born.day))

    return '{0} years'.format(age)


def humanize_date(value):
    return arrow.get(value).humanize()
