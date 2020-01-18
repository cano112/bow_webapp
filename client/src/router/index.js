import Vue from 'vue';
import VueRouter from 'vue-router';
import Bow from '../components/Bow.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Bow',
    component: Bow,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;
