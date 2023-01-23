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
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/Login')
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
      path: '/forms',
      component: () => import('../views/settings/SlackFormSettings'),
      beforeEnter: Auth.requireIsAdminAuth,
      name: 'SlackFormSettings',
    },
    {
      path: '/profile-page',
      name: 'ProfilePage',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/user/ProfilePage'),
    },
    {
      path: '/home',
      component: () => import('../views/Home'),
      beforeEnter: Auth.requireAuth,
      name: 'Home',
    },
    {
      path: '/reports',
      component: () => import('../views/Reports'),
      name: 'Reports',
    },
    {
      path: '/create-leads',
      name: 'CreateLeads',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/CreateLeads')
    },
    {
      path: '/update-leads',
      name: 'UpdateLeads',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/UpdateLeads')
    },
    {
      path: '/update-contacts',
      name: 'UpdateContacts',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/UpdateContacts')
    },
    {
      path: '/update-accounts',
      name: 'UpdateAccounts',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/UpdateAccounts')
    },
    {
      path: '/create-accounts',
      name: 'CreateAccounts',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/CreateAccounts')
    },
    {
      path: '/product-form',
      name: 'ProductForm',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/ProductForm')
    },
    {
      path: '/create-contacts',
      name: 'CreateContacts',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/CreateContacts')
    },
    {
      path: '/update-opportunity',
      name: 'UpdateOpportunity',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/UpdateOpportunity')
    },
    {
      path: '/create-opportunity',
      name: 'CreateOpportunity',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/CreateOpportunity')
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
      path: '/forecast',
      name: 'Forecast',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/Forecast')
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
      path: '/closed-won',
      name: 'ClosedWon',
      beforeEnter: Auth.requireAuth,
      component: () =>
        import('../views/settings/alerts/create/templates/ClosedWon'),
    },
    {
      path: '/stage-advanced',
      name: 'StageAdvanced',
      beforeEnter: Auth.requireAuth,
      component: () =>
        import('../views/settings/alerts/create/templates/StageAdvanced'),
    },
    {
      path: '/moved-to-commit',
      name: 'MovedToCommit',
      beforeEnter: Auth.requireAuth,
      component: () =>
        import('../views/settings/alerts/create/templates/MovedToCommit'),
    },
    {
      path: '/close-date-pushed',
      name: 'CloseDatePushed',
      beforeEnter: Auth.requireAuth,
      component: () =>
        import('../views/settings/alerts/create/templates/CloseDatePushed'),
    },
    {
      path: '/map',
      name: 'CustomizeLandingPage',
      beforeEnter: Auth.requireAuth,
      component: () => import('@/views/customize/CustomizeLandingPage'),
      children: [
        {
          path: 'required',
          name: 'Required',
          component: () => import('@/views/customize/Required')
        },
        {
          path: 'validation',
          name: 'ValidationRules',
          component: () => import('@/views/customize/ValidationRules')
        },
        {
          path: 'custom',
          name: 'Custom',
          component: () => import('@/views/customize/Custom')
        },
      ]
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
        {
          path: '/real-time',
          name: 'RealTime',
          component: () =>
            import(
              '../views/settings/alerts/create/templates/RealTime'
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
