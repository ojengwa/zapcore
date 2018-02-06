import Vue from 'vue';
import Router from 'vue-router';

const routerOptions = [
  {
    path: '/',
    component: 'Home',
  },
  {
    path: '/landing',
    component: 'HelloWorld',
  },
  {
    path: '*',
    component: 'NotFound',
  },
];

const routes = routerOptions.map(route => ({
  ...route,
  component: () =>
    import (`@/components/${route.component}.vue`),
}));

Vue.use(Router);

export default new Router({
  routes,
  mode: 'history',
});
