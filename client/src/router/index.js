import Vue from 'vue'
import Router from 'vue-router'
import LeadsIndex from '@/views/LeadsIndex'
import LeadShow from '@/views/LeadShow'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/leads',
      name: 'leads-index',
      component: LeadsIndex,
    },
    {
      path: '/leads/:id',
      name: 'lead-show',
      component: LeadShow,
      props: true,
    },
  ],
})
