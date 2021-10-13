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
import Notifications from '@/views/settings/Notifications'
import Configure from '@/views/auth/Configure'
import CustomizeLandingPage from '@/views/customize/CustomizeLandingPage'
import UpdateOpportunity from '@/views/customize/UpdateOpportunity'
import CreateContacts from '@/views/customize/CreateContacts'
import CreateOpportunity from '@/views/customize/CreateOpportunity'
import CreateAccounts from '@/views/customize/CreateAccounts'
import UpdateContacts from '@/views/customize/UpdateContacts'
import UpdateAccounts from '@/views/customize/UpdateAccounts'
import UpdateLeads from '@/views/customize/UpdateLeads'
import CreateLeads from '@/views/customize/CreateLeads'
import ProfilePage from '@/views/user/ProfilePage'
import CloseDateApproaching from '@/views/settings/alerts/create/templates/CloseDateApproaching'
import CloseDatePassed from '@/views/settings/alerts/create/templates/CloseDatePassed'
import DealRotting from '@/views/settings/alerts/create/templates/DealRotting'
import UpdateForecast from '@/views/settings/alerts/create/templates/UpdateForecast'

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
      path: '/notifications',
      name: 'Notifications',
      component: Notifications,
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
      beforeEnter: Auth.requireIsAdminAuth,
      name: 'SlackFormSettings',
    },
    {
      path: '/profile-page',
      name: 'ProfilePage',
      component: ProfilePage,
    },
    {
      path: '/create-leads',
      name: 'CreateLeads',
      component: CreateLeads,
    },
    {
      path: '/update-leads',
      name: 'UpdateLeads',
      component: UpdateLeads,
    },
    {
      path: '/update-contacts',
      name: 'UpdateContacts',
      component: UpdateContacts,
    },
    {
      path: '/update-accounts',
      name: 'UpdateAccounts',
      component: UpdateAccounts,
    },
    {
      path: '/create-accounts',
      name: 'CreateAccounts',
      component: CreateAccounts,
    },
    {
      path: '/configure',
      name: 'Configure',
      component: Configure
    },
    {
      path: '/create-contacts',
      name: 'CreateContacts',
      component: CreateContacts,
    },
    {
      path: '/update-opportunity',
      name: 'UpdateOpportunity',
      component: UpdateOpportunity
    },
    {
      path: '/customize',
      name: 'CustomizeLandingPage',
      component: CustomizeLandingPage,
    },
    {
      path: '/create-opportunity',
      name: 'CreateOpportunity',
      component: CreateOpportunity,
    },
    {
      path: '/close-date-passed',
      name: 'CloseDatePassed',
      component: CloseDatePassed,
    },
    {
      path: '/close-date-approaching',
      name: 'CloseDateApproaching',
      component: CloseDateApproaching,
    },
    {
      path: '/deal-rotting',
      name: 'DealRotting',
      component: DealRotting,
    },
    {
      path: '/update-forecast',
      name: 'UpdateForecast',
      component: UpdateForecast,
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
      ],
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
