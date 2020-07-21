import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import User from '@/services/users/'

Vue.use(Vuex)

const STORAGE_HASH = '{storage_hash}'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
  showSideNav: false,
  listenToSideNav: false,
}

const mutations = {
  UPDATE_USER: (state, payload) => {
    state.user = payload
  },
  UPDATE_USERTOKEN: (state, payload) => {
    state.token = payload
  },
  // Log out the user by resetting the state to defaults
  LOGOUT_USER(state) {
    state.token = null
    state.user = null
  },
  TOGGLE_SIDE_NAV(state, show) {
    state.showSideNav = show
  },
  TOGGLE_SIDE_NAV_LISTENER(state, listen) {
    state.listenToSideNav = listen
  },
}

const actions = {
  updateUser({ commit }, payload) {
    commit('UPDATE_USER', payload)
  },
  updateUserToken({ commit }, payload) {
    commit('UPDATE_USERTOKEN', payload)
  },
  logoutUser({ commit }) {
    commit('LOGOUT_USER')
  },
  refreshCurrentUser({ state, commit }) {
    if (!state.token) {
      return null
    }
    return User.api
      .getUser(state.user.id)
      .then(user => {
        commit('UPDATE_USER', user)
        return user
      })
      .catch(() => {
        // do nothing for now
        return null
      })
  },
}

const plugins = [
  createPersistedState({
    key: STORAGE_KEY,
  }),
]

const getters = {
  userIsLoggedIn: state => {
    return !!(state.token && state.user)
  },
  showSideNav: state => {
    return state.showSideNav
  },
  listenToSideNav: state => {
    return state.listenToSideNav
  },
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  plugins,
})
