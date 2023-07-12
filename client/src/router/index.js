// modules
import Vue from 'vue'
import Router from 'vue-router'
import Auth from '@/services/auth'
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
      component: () => import('@/views/settings/Settings')
    },
    {
      path: '/chat',
      name: 'Home',
      component: () => import('@/views/ChatHome')
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/Login')
    },
    {
      path: '/loginsignup',
      name: 'LoginOrSignup',
      component: () => import('@/views/auth/LoginOrSignup')
    },
    {
      path: '/admin-registration',
      name: 'AdminRegistration',
      component: () => import('@/views/auth/AdminRegistration')
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/auth/LeadershipCode')
    },
    {
      path: '/register-selection',
      name: 'RegisterSelection',
      component: () => import('@/views/auth/RegisterSelection')
    },
    {
      path: '/google-register',
      name: 'GoogleRegister',
      component: () => import('@/views/auth/GoogleRegister')
    },
    {
      path: '/auth/callback',
      name: 'AuthCallback',
      component: () => import('@/views/auth/AuthCallback'),
    },
    {
      path: '/activation/:userId/:magicToken',
      name: 'RepRegistration',
      component: () => import('@/views/auth/Register')
    },
    {
      path: '/activation/:uid/:token',
      name: 'Activation',
      component: () => import('@/views/auth/Activation')
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: () => import('@/views/auth/ForgotPassword'),
    },
    {
      path: '/resetpassword/:userId/:token',
      name: 'ResetPassword',
      component: () => import('@/views/auth/ResetPassword'),
  },
    {
      path: '/invite-users/:id?',
      props: true,
      name: 'InviteUsers',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/auth/InviteUsers'),
    },
    {
      path: '/profile-page',
      name: 'ProfilePage',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/user/ProfilePage'),
    },
    {
      path: '/reports',
      component: () => import('../views/Reports'),
      name: 'Reports',
    },
    {
      path: '/demo-center',
      component: () => import('../views/DemoCenter'),
      name: 'DemoCenter',
    },
    {
      path: '/forms',
      name: 'Forms',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/Forms')
    },
    {
      path: '/close-date-passed',
      name: 'CloseDatePassed',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/CloseDatePassed')
    },
    {
      path: '/next-step',
      name: 'UpcomingNextStep',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/NextStepDate')
    },
    {
      path: '/large-opps',
      name: 'LargeOpportunities',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/LargeOpps')
    },
    {
      path: '/empty-field',
      name: 'EmptyField',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/EmptyField')
    },
    {
      path: '/closing-this-month',
      name: 'ClosingThisMonth',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/ClosingThisMonth')
    },
    {
      path: '/closing-next-month',
      name: 'ClosingNextMonth',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/ClosingNextMonth')
    },
    {
      path: '/closing-this-quarter',
      name: 'ClosingThisQuarter',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/ClosingThisQuarter')
    },
    {
      path: '/team-pipeline',
      name: 'TeamPipeline',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/TeamPipeline')
    },
    {
      path: '/close-date-approaching',
      name: 'CloseDateApproaching',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/CloseDateApproaching')
    },
    {
      path: '/deal-rotting',
      name: 'DealReview',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/DealRotting')
    },
    {
      path: '/update-forecast',
      name: '30DayPipeline',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/UpdateForecast')
    },
    {
      path: '/log-zoom-meetings',
      name: 'LogZoom',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/LogZoom')
    },
    {
      path: '/recap-zoom-meetings',
      name: 'ZoomRecap',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/settings/alerts/create/templates/ZoomRecap')
    },
    {
      path: '/pipelines/:id?/:title?',
      props: true,
      name: 'Pipelines',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/Pipelines')
    },
    {
      path: '/meetings',
      name: 'Meetings',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/Meetings')
    },
    {
      path: '/notes',
      name: 'Notes',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/Notes')
    },
    {
      path: '/alerts',
      name: 'alerts',
      beforeEnter: Auth.requireAuth,
      component: () =>
        import(/* webpackChunkName: "settings" */ '../views/settings/alerts/AlertsDashboard'),
      children: [
        {
          path: 'templates',
          name: 'CreateNew',
          component: () =>
            import('../views/settings/alerts/create/AlertsPage'),
        },
        {
          path: 'build-your-own',
          name: 'BuildYourOwn',
          component: () =>
            import('../views/settings/alerts/create/BuildYourOwn'),
        },
        {
          path: 'list-templates',
          beforeEnter: Auth.requireAuth,
          name: 'ListTemplates',
          component: () =>
            import(
              /* webpackChunkName: "settings" */ '../views/settings/alerts/view/_AlertsTemplateList'
            ),
        },
      ],
    },
    {
      path: '/staff',
      name: 'Staff',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/staff/Staff')
    },
    {
      path: '/settings',
      component: () => import('@/views/settings/Settings'),
      beforeEnter: Auth.requireAuth,
      children: [
        {
          path: 'integrations',
          name: 'Integrations',
          component: () =>
            import('../views/auth/IntegrationScreen'),
        },
      ],
    },
  ],
})
