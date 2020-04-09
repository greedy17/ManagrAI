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
      name: 'Login',
      component: Login,
    },
    {
      path: '/invite',
      name: 'Invite',
      component: Invite,
    },
    {
      path: '/activation/:uid/:token',
      name: 'Activation',
      component: Activation,
    },
    {
      path: '/leads',
      name: 'LeadsIndex',
      component: LeadsIndex,
    },
    {
      path: '/leads/:id',
      name: 'LeadShow',
      component: LeadShow,
      props: true,
    },
  ],
})
