import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import * as Cookies from 'js-cookie'
import User from '@/services/users/'
import Status from '@/services/statuses'
// import { apiClient, apiErrorHandler } from '@/services/api'
import { MeetingWorkflows, SObjectPicklist, SObjects } from '@/services/salesforce/models'
import { ObjectField, CRMObjects } from '@/services/crm'

Vue.use(Vuex)

const STORAGE_HASH = '128adjfn2n'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
  stages: null,
  filters: [],
  meetings: [],
  showToolbarNav: false,
  pollingData: {
    items: {},
    lastCheck: null,
  },
  templates: null,
  pollingItems: [],
  pricebooks: null,
  allOpps: [],
  chatOpps: [],
  allContacts: [],
  allAccounts: [],
  allLeads: [],
  allPicklistOptions: null,
  apiPicklistOptions: null,
  shouldUpdatePollingData: false,
  itemsFromPollToUpdate: new Set(),
  customObject: {
    task: null,
    verboseName: null,
    checker: null,
  },
  recordTypes: [],
}

const mutations = {
  UPDATE_STAGES: (state, payload) => {
    state.stages = payload
  },
  UPDATE_USER: (state, payload) => {
    state.user = payload
  },
  UPDATE_FILTERS: (state, payload) => {
    state.filters = payload
  },
  UPDATE_USERTOKEN: (state, payload) => {
    state.token = payload
  },
  UPDATE_RECORD_TYPES: (state, payload) => {
    state.recordTypes = payload
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
  SAVE_CHAT_OPPS(state, chatOpps) {
    state.chatOpps = chatOpps
  },
  SAVE_ALL_CONTACTS(state, allContacts) {
    state.allContacts = allContacts
  },
  SAVE_ALL_LEADS(state, allLeads) {
    state.allLeads = allLeads
  },
  SAVE_ALL_ACCOUNTS(state, allAccounts) {
    state.allAccounts = allAccounts
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
  },
  UPDATE_CUSTOM_OBJECT: (state, payload) => {
    state.customObject = payload
  },

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
  changeFilters({ commit }, filters) {
    commit('UPDATE_FILTERS', filters)
  },
  async loadChatOpps({ state, commit }, page = 1) {
    let resourceName = ''
    if (state.user.crm === 'SALESFORCE') {
      resourceName = 'Opportunity'
    } else if (state.user.crm === 'HUBSPOT') {
      resourceName = 'Deal'
    } else {
      resourceName = 'Opportunity'
    }
    let oldResults = []
    if (page > 1) {
      oldResults = state.chatOpps.results
    }
    let res
    if (!state.filters.length) {
      res = await CRMObjects.api.getObjects(resourceName, page)
    } else {
      res = await CRMObjects.api.getObjects(resourceName, page, true, state.filters)
    }
    res.results = [...oldResults, ...res.results]
    commit('SAVE_CHAT_OPPS', res)
    return res
  },
  async loadAllOpps({ state, commit }, filters = []) {
    try {
      let res
      if (state.user.crm === 'SALESFORCE') {
        if (!filters.length) {
          filters = [['NOT_EQUALS', 'StageName', 'Closed Won'], ['NOT_EQUALS', 'StageName', 'Closed Lost']]
        }
        res = await CRMObjects.api.getObjectsForWorkflows('Opportunity', true, filters)
      } else {
        if (!filters.length) {
          filters = [['NOT_EQUALS', 'dealstage', 'closedwon'], ['NOT_EQUALS', 'dealstage', 'closedlost']]
        }
        res = await CRMObjects.api.getObjectsForWorkflows('Deal', true, filters)
      }
      commit('SAVE_ALL_OPPS', res.results)
      return res.results
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllAccounts({ state, commit }, filters = []) {
    try {
      let res
      if (state.user.crm === 'SALESFORCE') {
        res = await CRMObjects.api.getObjectsForWorkflows('Account', true, filters)
      } else {
        res = await CRMObjects.api.getObjectsForWorkflows('Company', true, filters)
      }
      commit('SAVE_ALL_ACCOUNTS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllContacts({ commit }, filters = []) {
    try {
      const res = await CRMObjects.api.getObjectsForWorkflows('Contact', true, filters)
      commit('SAVE_ALL_CONTACTS', res.results)
    } catch (e) {
      console.log(e)
    }
  },
  async loadAllLeads({ commit }, filters = []) {
    try {
      const res = await CRMObjects.api.getObjectsForWorkflows('Lead', true, filters)
      commit('SAVE_ALL_LEADS', res.results)
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
        if (res[i].fieldRef) {
          obj[res[i].fieldRef.id] = res[i].values
        }
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
        if (res[i].fieldRef) {
          obj[res[i].fieldRef.apiName] = res[i].values
        }
      }
    } catch (e) {
      console.log(e)
    } finally {

      commit('SAVE_API_PICKLISTS', obj)
    }
  },
  async checkTask({ commit }, vbName) {
    try {
      const task = await User.api.checkTasks(vbName)
      commit('UPDATE_CUSTOM_OBJECT', { ...state.customObject, task })
    } catch (e) {
      console.log(e)
    }
  },
  async setCustomObject({ commit, dispatch }, name) {
    try {
      await SObjects.api.getCustomObjectFields(name).then((res) => {
        const vbName = res.verbose_name
        // state.customObject.checker = setInterval(() => {
        //   dispatch('checkTask', vbName)
        //   // this.loaderText = this.loaderTextList[this.changeLoaderText()]
        // }, 2000)
        commit('UPDATE_CUSTOM_OBJECT', { ...state.customObject, task: null })
      })
    } catch (e) {
      console.log(e)
    }
  },
  async getRecords({ commit }) {
    const res = await SObjects.api.getRecords()
    commit('UPDATE_RECORD_TYPES', res)
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
    // storage: window.sessionStorage
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
