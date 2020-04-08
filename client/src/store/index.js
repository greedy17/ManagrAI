import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'

Vue.use(Vuex)

const STORAGE_HASH = '{storage_hash}'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
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
}

const actions = {
  updateUser({ commit }, payload) {
    commit('UPDATE_USER', payload)
  },
  updateUserToken({ commit }, payload) {
    commit('UPDATE_USERTOKEN', payload)
  },
}

const plugins = [
  createPersistedState({
    key: STORAGE_KEY,
  }),
]

const getters = {
  userIsLoggedIn: state => {
    return state.token && state.user
  },
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  plugins,
})
