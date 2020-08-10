import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import User from '@/services/users/'
import Status from '@/services/statuses'
import Polling from '@/services/polling'

Vue.use(Vuex)

const STORAGE_HASH = '{storage_hash}'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
  showSideNav: false,
  listenToSideNav: false,
  stages: null,
  showToolbarNav: false,
  pollingData: {
    notification: { count: 0, lastChecked: null },
  },
  pollingItems: [],
  shouldUpdatePollingData: false,
  itemsFromPollToUpdate: new Set(),
}

const mutations = {
  UPDATE_ITEMS_TO_POLL: (state, ...payload) => {
    payload.forEach(i => {
      let index = state.pollingItems.findIndex(item => item == i)
      if (index != -1) {
        state.pollingItems.slice(index, 1)
      } else {
        state.pollingItems.push(i)
      }
    })
  },
  UPDATE_STAGES: (state, payload) => {
    state.stages = payload
  },
  UPDATE_POLLING_DATA: (state, payload) => {
    let currentPollingData = { ...state.pollingData }
    for (const [key, value] of Object.entries(currentPollingData.items)) {
      state.itemsFromPollToUpdate = []
      if (payload.items[key]) {
        if (payload.items[key].count > value.count) {
          state.itemsFromPollToUpdate.push(key)
          state.shouldUpdatePollingData = true
        } else {
          state.shouldUpdatePollingData = false
        }
      }
    }
    state.pollingData = { ...payload }
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
  TOGGLE_SIDE_NAV(state, show) {
    state.showSideNav = show
  },
  TOGGLE_SIDE_TOOLBAR_NAV(state, show) {
    state.showToolbarNav = show
  },
  TOGGLE_SIDE_NAV_LISTENER(state, listen) {
    state.listenToSideNav = listen
  },
}

const actions = {
  async updateStages({ state, commit }) {
    if (!state.token) return null

    const res = await Status.api.list({})

    commit('UPDATE_STAGES', res.results ? res.results : null)
  },
  async updatePollingData({ state, commit }) {
    const res = await Polling.listPollingCount(state.pollingItems, state.pollingData.lastChecked)

    commit('UPDATE_POLLING_DATA', res)
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
  showSideNav: state => {
    return state.showSideNav
  },
  showToolbarNav: state => {
    return state.showToolbarNav
  },
  listenToSideNav: state => {
    return state.listenToSideNav
  },
  updatePollingData: state => {
    return state.shouldUpdatePollingData
  },
  pollingDataToUpdate: state => {
    return state.itemsFromPollToUpdate
  },
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  plugins,
})
