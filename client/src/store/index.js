import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import User from '@/services/users/'
import Status from '@/services/statuses'
// import { apiClient, apiErrorHandler } from '@/services/api'
import { MeetingWorkflows, SObjectPicklist, SObjects } from '@/services/salesforce/models'

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
  templates: null,
  pollingItems: [],
  pricebooks: null,
  allOpps: null,
  allPicklistOptions: null,
  apiPicklistOptions: null,
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
  SAVE_ALL_OPPS(state, allOpps) {
    state.allOpps = allOpps
  },
  SAVE_MEETINGS(state, meetings) {
    state.meetings = meetings
  },
  SAVE_TEMPLATES(state, templates) {
    state.templates = templates
  },
  SAVE_PRICEBOOKS(state, pricebooks) {
    state.pricebooks = pricebooks
  },
  SAVE_ALL_PICKLISTS(state, allPicklistOptions) {
    state.allPicklistOptions = allPicklistOptions;
  },
  SAVE_API_PICKLISTS(state, apiPicklistOptions) {
    state.apiPicklistOptions = apiPicklistOptions;
  }

}

const actions = {
  async updateStages({ state, commit }) {
    if (!state.token) return null

    const res = await Status.api.list({})

    commit('UPDATE_STAGES', res.results ? res.results : null)
  },
  async loadTemplates({ commit }) {
    try {
      const res = await User.api.getTemplates()
      commit('SAVE_TEMPLATES', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadMeetings({ commit }) {
    try {
      const res = await MeetingWorkflows.api.getMeetingList()
      commit('SAVE_MEETINGS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllOpps({ commit }, filters = [['NOT_EQUALS', 'StageName', 'Closed Won'],['NOT_EQUALS', 'StageName', 'Closed Lost'],]) {
    try {
      const res = await SObjects.api.getObjectsForWorkflows('Opportunity', true, filters)
      commit('SAVE_ALL_OPPS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadPricebooks({ commit }) {
    try {
      const res = await SObjects.api.getObjects('Pricebook2')
      commit('SAVE_PRICEBOOKS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllPicklists({ commit }) {
    let obj = {}

    try {
      const res = await SObjectPicklist.api.listPicklists({ pageSize: 1000 })
      for (let i = 0; i < res.length; i++) {
        obj[res[i].fieldRef.id] = res[i].values
      }
    } catch (e) {
      console.log(e)
    } finally {

      commit('SAVE_ALL_PICKLISTS', obj)
    }
  },
  async loadApiPicklists({ commit }) {
    let obj = {}

    try {
      const res = await SObjectPicklist.api.listPicklists({ pageSize: 1000 })
      for (let i = 0; i < res.length; i++) {
        obj[res[i].fieldRef.apiName] = res[i].values
      }
    } catch (e) {
      console.log(e)
    } finally {

      commit('SAVE_API_PICKLISTS', obj)
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
