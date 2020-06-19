// modules
import Vue from 'vue'
import Router from 'vue-router'

// auth
import Auth from '@/services/auth'

// views
import Login from '@/views/auth/Login'
import Invite from '@/views/auth/Invite'
import Activation from '@/views/auth/Activation'
import LeadsIndex from '@/views/leads/LeadsIndex'
import LeadsDetail from '@/views/leads/LeadsDetail'
import LeadsNew from '@/views/leads/LeadsNew'
import Prospect from '@/views/leads/Prospect'
import Forecast from '@/views/leads/Forecast'
import Nylas from '@/views/nylas-integration/Nylas'
import NylasCallback from '@/views/nylas-integration/NylasCallback'
import Settings from '@/views/settings/Settings'
// import Styles from '@/views/settings/Styles'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      beforeEnter: Auth.homepageRedirect,
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
      beforeEnter: Auth.requireAuth,
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
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/leads/new',
      name: 'LeadsNew',
      component: LeadsNew,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/leads/:id',
      name: 'LeadsDetail',
      component: LeadsDetail,
      props: true,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/prospect',
      name: 'Prospect',
      component: Prospect,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/forecast',
      name: 'Forecast',
      component: Forecast,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/nylas',
      name: 'Nylas',
      component: Nylas,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/nylas/callback',
      name: 'NylasCallback',
      component: NylasCallback,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/settings',
      name: 'Settings',
      component: Settings,
      beforeEnter: Auth.requireAuth,
    },
    // {
    //   path: '/styles',
    //   name: 'Styles',
    //   component: Styles,
    //   beforeEnter: Auth.requireAuth,
    // },
  ],
})
