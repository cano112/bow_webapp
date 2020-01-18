import Vue from 'vue';
import { BootstrapVue, IconsPlugin, SpinnerPlugin } from 'bootstrap-vue';
import App from './App.vue';
import router from './router';
import 'bootstrap/dist/css/bootstrap.css';

Vue.use(BootstrapVue);
Vue.use(IconsPlugin);
Vue.use(SpinnerPlugin);

Vue.config.productionTip = false;

new Vue({
  router,
  render: h => h(App),
}).$mount('#app');
