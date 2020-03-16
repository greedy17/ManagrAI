import Vue from 'vue'
import Router from 'vue-router'
import LeadsIndex from '@/views/LeadsIndex'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/leads',
      name: 'leads-index',
      component: LeadsIndex,
    },
  ],
})
