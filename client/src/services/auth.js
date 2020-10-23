import store from '@/store'

export default {
  getHeaders,
  requireAuth,
  homepageRedirect,
  requireUserTypeManagerOrStaff,
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
  if (!store.getters.userIsLoggedIn) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
  } else if (!store.state.user.isStaff && !store.state.user.isManager) {
    next({
      name: 'Settings',
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
 * @function    homepageRedirect
 * @description specific to the root route: vue-router beforeEnter-style function to check user auth
 *              status and redirect appropriately.
 */
function homepageRedirect(to, from, next) {
  if (!store.getters.userIsLoggedIn) {
    next({
      name: 'Login',
    })
  } else {
    next({
      name: 'LeadsIndex',
    })
  }
}
