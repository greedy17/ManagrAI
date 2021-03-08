import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import User from '@/services/users/'
import Status from '@/services/statuses'

Vue.use(Vuex)

const STORAGE_HASH = '128adjfn2n'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
  stages: null,
  showToolbarNav: false,
  pollingData: {
    items: {},
    lastCheck: null,
  },
  pollingItems: [],
  shouldUpdatePollingData: false,
  itemsFromPollToUpdate: new Set(),
}

const mutations = {
  UPDATE_STAGES: (state, payload) => {
    state.stages = payload
  },
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
    state.stages = []
  },
}

const actions = {
  async updateStages({ state, commit }) {
    if (!state.token) return null

    const res = await Status.api.list({})

    commit('UPDATE_STAGES', res.results ? res.results : null)
  },
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
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  plugins,
})
