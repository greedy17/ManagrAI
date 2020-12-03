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
import Profile from '@/views/settings/_pages/_Profile'
import Invite from '@/views/settings/_pages/_Invite'
// import Password from '@/views/settings/_pages/_Password'
import NotificationSettings from '@/views/settings/_pages/_NotificationSettings'
import SlackIntegration from '@/views/settings/_pages/_SlackIntegration'
import SlackCallback from '@/views/settings/_pages/_SlackCallback'

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
      /*
        NOTE:
        The route name is removed due to the following warning:
        [vue-router] Named Route 'Settings' has a default child route.
        When navigating to this named route (:to="{name: 'Settings'"),
        the default child route will not be rendered. Remove the name from
        this route and use the name of the default child route for named links instead.
       */
      // name: 'Settings',
      component: Settings,
      beforeEnter: Auth.requireAuth,
      children: [
        {
          path: 'slack-integration/callback',
          name: 'SlackCallback',
          components: {
            'user-settings': SlackCallback,
          },
        },
        {
          path: 'slack-integration',
          name: 'SlackIntegration',
          components: {
            'user-settings': SlackIntegration,
          },
        },
        {
          path: 'zoom-integration',
          name: 'ZoomIntegration',
          components: {
            'user-settings': () =>
              import(
                /* webpackChunkName: "settings" */ '../views/settings/_pages/_ZoomIntegration'
              ),
          },
        },
        {
          path: 'text-integration',
          name: 'TextIntegration',
          components: {
            'user-settings': () =>
              import(
                /* webpackChunkName: "settings" */ '../views/settings/_pages/_TextIntegration'
              ),
          },
        },
        {
          path: 'email-integration',
          name: 'EmailIntegration',
          components: {
            'user-settings': EmailIntegration,
          },
        },
        {
          path: 'email-templates',
          name: 'EmailTemplates',
          components: {
            'user-settings': EmailTemplates,
          },
        },
        {
          path: 'profile',
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
        {
          path: 'notification-settings',
          name: 'NotificationSettings',
          components: { 'user-settings': NotificationSettings },
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
