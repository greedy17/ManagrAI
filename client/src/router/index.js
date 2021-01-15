// modules
import Vue from 'vue'
import Router from 'vue-router'
import Auth from '@/services/auth'

// Auth Views
import Activation from '@/views/auth/Activation'
import Login from '@/views/auth/Login'
import Register from '@/views/auth/Register'

// Pages tied to integration flows
import Integrations from '@/views/Integrations'
import Nylas from '@/views/nylas-integration/Nylas'
import NylasCallback from '@/views/nylas-integration/NylasCallback'
import ZoomPage from '@/views/zoom/ZoomPage'
import SlackIntegration from '@/views/settings/_pages/_SlackIntegration'
import SlackCallback from '@/views/settings/_pages/_SlackCallback'
// TODO: Add pages for Salesforce integration
// Settigns-related views
import Settings from '@/views/settings/Settings'
import EmailIntegration from '@/views/settings/_pages/_EmailIntegration'
import EmailTemplates from '@/views/settings/_pages/_EmailTemplates'
import Profile from '@/views/settings/_pages/_Profile'
import Invite from '@/views/settings/_pages/_Invite'

// TODO: We should keep this style guide page
// import Styles from '@/views/settings/Styles'
// END TODO

// TODO 2020-01-13 William: The following components should no longer be necessary.
//      Once we confirm this, remove them
// import NotificationSettings from '@/views/settings/_pages/_NotificationSettings'
// import Password from '@/views/settings/_pages/_Password'
// import LeadsIndex from '@/views/leads/LeadsIndex'
// import LeadsDetail from '@/views/leads/LeadsDetail'
// import LeadsNew from '@/views/leads/LeadsNew'
// import Prospect from '@/views/leads/Prospect'
// import Forecast from '@/views/leads/Forecast'
// import Reports from '@/views/reports/Reports'
// import StoryReportDetail from '@/views/reports/StoryReportDetail'
// import PerformanceReportDetail from '@/views/reports/PerformanceReportDetail'
// END TODO

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
      path: '/register',
      name: 'Register',
      component: Register,
    },
    {
      path: '/activation/:uid/:token',
      name: 'Activation',
      component: Activation,
    },

    // END TODO

    // {
    //   path: '/leads',
    //   name: 'LeadsIndex',
    //   component: LeadsIndex,
    //   beforeEnter: Auth.requireAuth,
    // },
    {
      path: '/meetings',
      name: 'Meetings',
      component: ZoomPage,
      beforeEnter: Auth.requireAuth,
    },
    // {
    //   path: '/leads/new',
    //   name: 'LeadsNew',
    //   component: LeadsNew,
    //   beforeEnter: Auth.requireAuth,
    // },
    // {
    //   path: '/leads/:id',
    //   name: 'LeadsDetail',
    //   component: LeadsDetail,
    //   props: true,
    //   beforeEnter: Auth.requireAuth,
    // },
    // {
    //   path: '/prospect',
    //   name: 'Prospect',
    //   component: Prospect,
    //   beforeEnter: Auth.requireAuth,
    // },
    // {
    //   path: '/forecast',
    //   name: 'Forecast',
    //   component: Forecast,
    //   beforeEnter: Auth.requireAuth,
    // },
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
      component: Settings,
      //beforeEnter: Auth.requireAuth,
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
          beforeEnter: Auth.requireUserTypeManagerOrStaff,
        },
        // {
        //   path: 'notification-settings',
        //   name: 'NotificationSettings',
        //   components: { 'user-settings': NotificationSettings },
        // },
        { path: '', redirect: '/settings/email-integration' },
      ],
    },
    // {
    //   path: '/reports',
    //   name: 'Reports',
    //   component: Reports,
    //   beforeEnter: Auth.requireAuth,
    // },
    // {
    //   path: '/story-reports/:id',
    //   name: 'StoryReportDetail',
    //   props: true,
    //   component: StoryReportDetail,
    //   beforeEnter: Auth.requireAuth,
    // },
    // {
    //   path: '/performance-reports/:id',
    //   name: 'PerformanceReportDetail',
    //   props: true,
    //   component: PerformanceReportDetail,
    //   beforeEnter: Auth.requireAuth,
    // },
    // {
    //   path: '/styles',
    //   name: 'Styles',
    //   component: Styles,
    //   beforeEnter: Auth.requireAuth,
    // },
  ],
})
