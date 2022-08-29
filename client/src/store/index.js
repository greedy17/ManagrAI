import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import User from '@/services/users/'
import Status from '@/services/statuses'
// import { apiClient, apiErrorHandler } from '@/services/api'
import { MeetingWorkflows } from '@/services/salesforce'

Vue.use(Vuex)

const STORAGE_HASH = '128adjfn2n'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
  stages: null,
  meetings: [],
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
  SAVE_MEETINGS(state, meetings) {
    state.meetings = meetings
  },
}

const actions = {
  async updateStages({ state, commit }) {
    if (!state.token) return null

    const res = await Status.api.list({})

    commit('UPDATE_STAGES', res.results ? res.results : null)
  },
  async loadMeetings({ commit }) {
    try {
      const res = await MeetingWorkflows.api.getMeetingList()
      commit('SAVE_MEETINGS', res.results)
    } catch (e) {
      console.log(e)
      // this.$toast('Error gathering Meetings!', {
      //   timeout: 2000,
      //   position: 'top-left',
      //   type: 'error',
      //   toastClassName: 'custom',
      //   bodyClassName: ['custom'],
      // })
    }
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
