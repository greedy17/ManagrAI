import store from '@/store'
import { decryptData } from '../encryption'

export default {
  getHeaders,
  requireAuth,
  homepageRedirect,
  requireUserTypeManagerOrStaff,
  requireIsAdminAuth,
}

//  NOTE(Bruno 4-8-20): login/logout functionality is within the UserAPI.

function getHeaders() {
  if (!store.state.token) {
    return {}
  }
  return {
    Authorization: `Token ${store.state.token}`,
  }
}

/**
 * @function    requireUserTypeManager
 * @description vue-router beforeEnter-style function to check user auth
 *              status and redirect appropriately.
 */
function requireUserTypeManagerOrStaff(to, from, next) {
  const decryptedUser = decryptData(store.state.user, process.env.VUE_APP_SECRET_KEY)
  if (!store.getters.userIsLoggedIn) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
  } else if (!decryptedUser.isStaff && !decryptedUser.isManager) {
    next({
      name: 'EmailIntegration',
    })
  } else {
    next()
  }
}

/**
 * @function    requireAuth
 * @description vue-router beforeEnter-style function to check user auth
 *              status and redirect appropriately.
 */
function requireAuth(to, from, next) {
  if (!store.getters.userIsLoggedIn) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
  } else {
    next()
  }
}
/**
 * @function    requireIsAdminAuth
 * @description vue-router beforeEnter-style function to check user auth
 *              status and see if they are the isAdmin user redirect appropriately.
 */
function requireIsAdminAuth(to, from, next) {
  const decryptedUser = decryptData(store.state.user, process.env.VUE_APP_SECRET_KEY)
  if (!store.getters.userIsLoggedIn) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
  } else if (!decryptedUser.isAdmin) {
    next({
      name: 'ListTemplates',
      query: { redirect: to.fullPath },
    })
  } else {
    next()
  }
}

/**
 * @function    homepageRedirect
 * @description specific to the root route: vue-router beforeEnter-style function to check user auth
 *              status and redirect appropriately.
 */
function homepageRedirect(to, from, next) {
  if (!store.getters.userIsLoggedIn) {
    next({
      name: 'LoginOrSignup',
    })
  } else {
    next({
      name: 'ListTemplates',
    })
  }
}
