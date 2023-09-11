// modules
import Vue from 'vue'
import Router from 'vue-router'
import Auth from '@/services/auth'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      beforeEnter: Auth.homepageRedirect,
      component: () => import('@/views/ChatHome')
    },
    {
      path: '/chat',
      name: 'Home',
      component: () => import('@/views/ChatHome')
    },
    {
      path: '/summaries',
      name: 'PRSummaries',
      component: () => import('@/views/PRSummaries')
    },
    {
      path: '/pitches',
      name: 'Pitches',
      component: () => import('@/views/Pitches'),
    },
    {
      path: '/transcribe',
      name: 'PRTranscripts',
      component: () => import('@/views/PRTranscripts'),
    },
    {
      path: '/pr-integrations',
      name: 'PRIntegrations',
      component: () => import('@/views/PRIntegrations')
    },
    {
      path: '/reports',
      name: 'PRReports',
      component: () => import('@/views/PRReports')
    },
    {
      path: '/pr-settings',
      name: 'PRSettings',
      component: () => import('@/views/PRSettings')
    },
    {
      path: '/clip-report',
      name: 'PRClipReport',
      component: () => import('@/views/PRClipReport')
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
      path: '/shared/:code?',
      name: 'SharedReport',
      component: () => import('../components/pr/SharedReport')
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
    // {
    //   path: '/activation/:userId/:magicToken',
    //   name: 'RepRegistration',
    //   component: () => import('@/views/auth/Register')
    // },
    {
      path: '/activation/:code',
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
