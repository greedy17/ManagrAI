import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/views/auth/Login'
import Invite from '@/views/auth/Invite'
import Activation from '@/views/auth/Activation'
import LeadsIndex from '@/views/leads/LeadsIndex'
import LeadsDetail from '@/views/leads/LeadsDetail'
import LeadsNew from '@/views/leads/LeadsNew'

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
      path: '/leads/new',
      name: 'LeadsNew',
      component: LeadsNew,
    },
    {
      path: '/leads/:id',
      name: 'LeadsDetail',
      component: LeadsDetail,
      props: true,
    },
  ],
})
