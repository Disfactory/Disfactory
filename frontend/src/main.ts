import Vue from 'vue'
import App from './App.vue'
import VueCompositionApi from '@vue/composition-api'
import './registerServiceWorker'

Vue.config.productionTip = false
Vue.use(VueCompositionApi)

new Vue({
  render: (h) => h(App)
}).$mount('#app')
