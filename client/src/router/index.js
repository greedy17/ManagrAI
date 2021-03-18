// modules
import Vue from 'vue'
import Router from 'vue-router'
import Auth from '@/services/auth'

// Auth Views
import Activation from '@/views/auth/Activation'
import Login from '@/views/auth/Login'
import AdminRegistration from '@/views/auth/AdminRegistration'
import LeadershipCode from '@/views/auth/LeadershipCode'
import InviteUsers from '@/views/auth/InviteUsers'
import IntegrationScreen from '@/views/auth/IntegrationScreen'
import ForgotPassword from '@/views/auth/ForgotPassword'
import ResetPassword from '@/views/auth/ResetPassword'
import Register from '@/views/auth/Register'

// TODO: Add pages for Salesforce integration
// Settigns-related views
import Settings from '@/views/settings/Settings'
import Profile from '@/views/settings/_pages/_Profile'
import Invite from '@/views/settings/_pages/_Invite'
import SlackFormSettings from '../views/settings/SlackFormSettings'

// TODO: We should keep this style guide page
// import Styles from '@/views/settings/Styles'
// END TODO

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      beforeEnter: Auth.homepageRedirect,
      component: Settings,
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
    },
    {
      path: '/admin-registration',
      name: 'AdminRegistration',
      component: AdminRegistration,
    },
    {
      path: '/register',
      name: 'Register',
      component: LeadershipCode,
    },
    {
      path: '/activation/:userId/:magicToken',
      name: 'RepRegistration',
      component: Register,
    },
    {
      path: '/activation/:uid/:token',
      name: 'Activation',
      component: Activation,
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPassword,
    },
    {
      path: '/resetpassword/:userId/:token',
      name: 'ResetPassword',
      component: ResetPassword,
    },
    {
      path: '/invite-users',
      name: 'InviteUsers',
      component: InviteUsers,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/forms',
      component: SlackFormSettings,

      beforeEnter: Auth.requireAuth,
      name: 'SlackFormSettings',
    },

    {
      path: '/settings',
      component: Settings,
      beforeEnter: Auth.requireAuth,
      children: [
        {
          path: 'integrations',
          name: 'Integrations',
          component: () =>
            import(/* webpackChunkName: "settings" */ '../views/auth/IntegrationScreen'),
        },
      ],
    },
    //
    // {
    //   path: '/styles',
    //   name: 'Styles',
    //   component: Styles,
    //   beforeEnter: Auth.requireAuth,
    // },
    // {
  ],
})
