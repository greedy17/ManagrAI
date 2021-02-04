// modules
import Vue from 'vue'
import Router from 'vue-router'
import Auth from '@/services/auth'

// Auth Views
import Activation from '@/views/auth/Activation'
import Login from '@/views/auth/Login'
import Register from '@/views/auth/Register'

// TODO: Add pages for Salesforce integration
// Settigns-related views
import Settings from '@/views/settings/Settings'
import Profile from '@/views/settings/_pages/_Profile'
import Invite from '@/views/settings/_pages/_Invite'

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
      path: '/register',
      name: 'Register',
      component: Register,
    },
    {
      path: '/activation/:uid/:token',
      name: 'Activation',
      component: Activation,
    },

    {
      path: '/settings',
      component: Settings,
      beforeEnter: Auth.requireAuth,
      children: [
        {
          path: 'integrations',
          name: 'Integrations',
          components: {
            'user-settings': () =>
              import(/* webpackChunkName: "settings" */ '../views/Integrations'),
          },
        },

        {
          path: '',
          name: 'Profile',
          components: {
            'user-settings': Profile,
          },
        },
        // NOTE (Bruno 6-18-2020) once we get password-reset-flow incorporated, we can add the Password page
        // {
        //   path: 'password',
        //   name: 'Password',
        //   components: {
        //     'user-settings': Password,
        //   },
        // },
        {
          path: 'invite',
          name: 'Invite',
          components: { 'user-settings': Invite },
          //beforeEnter: Auth.requireUserTypeManagerOrStaff,
        },
        // {
        //   path: 'notification-settings',
        //   name: 'NotificationSettings',
        //   components: { 'user-settings': NotificationSettings },
        // },
      ],
    },
    //
    // {
    //   path: '/styles',
    //   name: 'Styles',
    //   component: Styles,
    //   beforeEnter: Auth.requireAuth,
    // },
  ],
})
