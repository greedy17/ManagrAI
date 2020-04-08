import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/views/Login'
import Invite from '@/views/Invite'
import Activation from '@/views/Activation'
import LeadsIndex from '@/views/LeadsIndex'
import LeadShow from '@/views/LeadShow'

//TODO(Bruno 4-8-20): lazy-load views

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/leads',
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/invite',
      name: 'invite',
      component: Invite,
    },
    {
      path: '/activation/:uid/:token',
      name: 'activation',
      component: Activation,
    },
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
