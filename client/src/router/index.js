// modules
import Vue from 'vue'
import Router from 'vue-router'

// auth
import Auth from '@/services/auth'

// views
import Login from '@/views/auth/Login'
import Activation from '@/views/auth/Activation'
import LeadsIndex from '@/views/leads/LeadsIndex'
import LeadsDetail from '@/views/leads/LeadsDetail'
import LeadsNew from '@/views/leads/LeadsNew'
import Prospect from '@/views/leads/Prospect'
import Forecast from '@/views/leads/Forecast'
import Nylas from '@/views/nylas-integration/Nylas'
import NylasCallback from '@/views/nylas-integration/NylasCallback'
import Reports from '@/views/reports/Reports'
import StoryReportDetail from '@/views/reports/StoryReportDetail'
import PerformanceReportDetail from '@/views/reports/PerformanceReportDetail'
// import Styles from '@/views/settings/Styles'

// settings -related views
import Settings from '@/views/settings/Settings'
import EmailIntegration from '@/views/settings/_pages/_EmailIntegration'
import EmailTemplates from '@/views/settings/_pages/_EmailTemplates'
import TextIntegration from '@/views/settings/_pages/_TextIntegration'
import Profile from '@/views/settings/_pages/_Profile'
import Invite from '@/views/settings/_pages/_Invite'
// import Password from '@/views/settings/_pages/_Password'
import NotificationSettings from '@/views/settings/_pages/_NotificationSettings'
import SlackIntegration from '@/views/settings/_pages/_SlackIntegration'

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
      // name: 'Settings',
      component: Settings,
      beforeEnter: Auth.requireAuth,
      children: [
        {
          name: 'EmailIntegration',
          path: 'email-integration',
          component: EmailIntegration,
        },
        {
          name: 'EmailTemplates',
          path: 'email-templates',
          component: EmailTemplates,
        },
        {
          name: 'TextIntegration',
          path: 'text-integration',
          component: TextIntegration,
        },
        {
          name: 'Profile',
          path: 'profile',
          component: Profile,
        },
        {
          name: 'Invite',
          path: 'invite',
          component: Invite,
          beforeEnter: Auth.requireUserTypeManagerOrStaff,
        },
        // NOTE (Bruno 6-18-2020) once we get password-reset-flow incorporated, we can add the Password page
        // {
        //   name: 'Password',
        //   path: 'password',
        //   component: Password,
        // },
        {
          name: 'NotificationSettings',
          path: 'notification-settings',
          component: NotificationSettings,
        },
        {
          name: 'SlackIntegration',
          path: 'slack-integration',
          component: SlackIntegration,
        },
        { path: '', redirect: '/settings/email-integration' },
      ],
    },
    {
      path: '/reports',
      name: 'Reports',
      component: Reports,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/story-reports/:id',
      name: 'StoryReportDetail',
      props: true,
      component: StoryReportDetail,
      beforeEnter: Auth.requireAuth,
    },
    {
      path: '/performance-reports/:id',
      name: 'PerformanceReportDetail',
      props: true,
      component: PerformanceReportDetail,
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
