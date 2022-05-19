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
      path: '/invite-users',
      name: 'InviteUsers',
      component: () => import('@/views/auth/InviteUsers'),
      beforeEnter: Auth.requireAuth,
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
      component: () => import('@/views/user/ProfilePage'),
    },
    {
      path: '/create-leads',
      name: 'CreateLeads',
      component: () => import('@/views/customize/CreateLeads')
    },
    {
      path: '/update-leads',
      name: 'UpdateLeads',
      component: () => import('@/views/customize/UpdateLeads')
    },
    {
      path: '/update-contacts',
      name: 'UpdateContacts',
      component: () => import('@/views/customize/UpdateContacts')
    },
    {
      path: '/update-accounts',
      name: 'UpdateAccounts',
      component: () => import('@/views/customize/UpdateAccounts')
    },
    {
      path: '/create-accounts',
      name: 'CreateAccounts',
      component: () => import('@/views/customize/CreateAccounts')
    },
    {
      path: '/product-form',
      name: 'ProductForm',
      component: () => import('@/views/customize/ProductForm')
    },
    {
      path: '/create-contacts',
      name: 'CreateContacts',
      component: () => import('@/views/customize/CreateContacts')
    },
    {
      path: '/update-opportunity',
      name: 'UpdateOpportunity',
      component: () => import('@/views/customize/UpdateOpportunity')
    },
    {
      path: '/create-opportunity',
      name: 'CreateOpportunity',
      component: () => import('@/views/customize/CreateOpportunity')
    },
    {
      path: '/close-date-passed',
      name: 'CloseDatePassed',
      component: () => import('@/views/settings/alerts/create/templates/CloseDatePassed')
    },
    {
      path: '/next-step',
      name: 'NextStep',
      component: () => import('@/views/settings/alerts/create/templates/NextStepDate')
    },
    {
      path: '/large-opps',
      name: 'LargeOpps',
      component: () => import('@/views/settings/alerts/create/templates/LargeOpps')
    },
    {
      path: '/empty-field',
      name: 'RequiredFieldEmpty',
      component: () => import('@/views/settings/alerts/create/templates/RequiredFieldEmpty')
    },
    {
      path: '/close-date-approaching',
      name: 'CloseDateApproaching',
      component: () => import('@/views/settings/alerts/create/templates/CloseDateApproaching')
    },
    {
      path: '/deal-rotting',
      name: 'DealRotting',
      component: () => import('@/views/settings/alerts/create/templates/DealRotting')
    },
    {
      path: '/update-forecast',
      name: 'UpdateForecast',
      component: () => import('@/views/settings/alerts/create/templates/UpdateForecast')
    },
    {
      path: '/log-zoom-meetings',
      name: 'LogZoom',
      component: () => import('@/views/settings/alerts/create/templates/LogZoom')
    },
    {
      path: '/recap-zoom-meetings',
      name: 'ZoomRecap',
      component: () => import('@/views/settings/alerts/create/templates/ZoomRecap')
    },
    {
      path: '/pipelines/:id?/',
      props: true,
      name: 'Pipelines',
      component: () => import('@/views/Pipelines')
    },
    {
      path: '/meetings',
      name: 'Meetings',
      component: () => import('@/views/Meetings')
    },
    {
      path: '/staff',
      name: "Staff",
      component: () =>
        import("@/views/staff/Staff")
    },
    {
      path: '/deal-movement',
      name: 'DealMovement',
      component: () =>
        import('../views/settings/alerts/create/templates/DealMovement'),
    },
    {
      path: '/closed-won',
      name: 'ClosedWon',
      component: () =>
        import('../views/settings/alerts/create/templates/ClosedWon'),
    },
    {
      path: '/map',
      name: 'CustomizeLandingPage',
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
      component: () =>
        import(/* webpackChunkName: "settings" */ '../views/settings/alerts/AlertsDashboard'),
      beforeEnter: Auth.requireAuth,
      children: [
        {
          path: 'templates',
          name: 'CreateNew',
          component: () =>
            import(/* webpackChunkName: "settings" */ '../views/settings/alerts/create/AlertsPage'),
        },
        {
          path: 'build-your-own',
          name: 'BuildYourOwn',
          component: () =>
            import(/* webpackChunkName: "settings" */ '../views/settings/alerts/create/BuildYourOwn'),
        },
        {
          path: 'list-templates',
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
            /* webpackChunkName: "settings" */ '../views/settings/alerts/create/templates/RealTime'
            ),
        },
      ],
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
