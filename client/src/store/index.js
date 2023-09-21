import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import * as Cookies from 'js-cookie'
import User from '@/services/users/'
import Status from '@/services/statuses'
// import { apiClient, apiErrorHandler } from '@/services/api'
import { MeetingWorkflows, SObjectPicklist, SObjects } from '@/services/salesforce/models'
import { Comms } from '@/services/comms'
import { ObjectField, CRMObjects } from '@/services/crm'
import { decryptData, encryptData } from '../encryption'

Vue.use(Vuex)

const STORAGE_HASH = '128adjfn2n'
export const STORAGE_KEY = `managr-${STORAGE_HASH}`

const state = {
  user: null,
  token: null,
  googleSignIn: {},
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
  messages: [],
  crmForms: [],
  currentView: 'home',
  currentMeeting: null,
  currentOpp: null,
  allPicklistOptions: null,
  apiPicklistOptions: null,
  shouldUpdatePollingData: false,
  itemsFromPollToUpdate: new Set(),
  meetingData: {},
  customObject: {
    task: null,
    verboseName: null,
    checker: null,
  },
  recordTypes: [],
  selectedArticle: null,
  chatTitle: 'All Open Opportunities',
  currentTask: null,
  meetingBeingProcessed: '',
  allSearches: [],
  allPitches: [],
  currentSearch: null,
  currentPitch: null,
  tempRefreshUser: null,
  generatedContent: null,
}

const mutations = {
  setGeneratedContent(state, payload) {
    state.generatedContent = payload;
  },
  UPDATE_STAGES: (state, payload) => {
    state.stages = payload
  },
  UPDATE_USER: (state, payload) => {
    state.user = payload
  },
  UPDATE_TEMP_REFRESH_USER: (state, payload) => {
    state.tempRefreshUser = payload
  },
  UPDATE_GOOGLE_SIGN_IN: (state, payload) => {
    state.googleSignIn = payload
  },
  UPDATE_FILTERS: (state, payload) => {
    state.filters = payload
  },
  UPDATE_SELECTED_ARTICLE: (state, payload) => {
    state.selectedArticle = payload
  },
  UPDATE_USERTOKEN: (state, payload) => {
    state.token = payload
  },
  UPDATE_RECORD_TYPES: (state, payload) => {
    state.recordTypes = payload
  },
  UPDATE_CHAT_TITLE: (state, payload) => {
    state.chatTitle = payload
  },
  UPDATE_TASK: (state, payload) => {
    state.currentTask = payload
  },
  UPDATE_MEETING_NAME: (state, payload) => {
    state.meetingBeingProcessed = payload
  },
  // Log out the user by resetting the state to defaults
  LOGOUT_USER(state) {
    state.token = null
    state.user = null
    state.currentTask = null
    state.currentView = 'home'
    state.meetingBeingProcessed = null
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
  SAVE_CRM_FORMS(state, crmForms) {
    state.crmForms = crmForms
  },
  SAVE_MEETINGS(state, meetings) {
    state.meetings = meetings
  },
  SAVE_SEARCHES(state, searches) {
    state.allSearches = searches
  },
  SAVE_PITCHES(state, pitches) {
    state.allPitches = pitches
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
  UPDATE_MESSAGES: (state, payload) => {
    state.messages.push(payload)
  },
  SET_VIEW: (state, payload) => {
    state.currentView = payload
  },
  SET_SEARCH: (state, payload) => {
    state.currentSearch = payload
  },
  SET_PITCH: (state, payload) => {
    state.currentPitch = payload
  },
  SET_MEETING: (state, payload) => {
    state.currentMeeting = payload
  },
  SET_OPP: (state, payload) => {
    state.currentOpp = payload
  },
  SET_MEETING_DATA: (state, { id, data }) => {
    let newData = {}
    newData['data'] = data
    state.meetingData[id] = newData
  },
  EDIT_MEETING: (state, { id, updated }) => {
    let newData
    newData = state.meetingData[id]
    newData['updated'] = updated
    state.meetingData[id] = newData
  },
  EDIT_MESSAGES: (state, {
    id,
    value,
    gtMsg,
    generated,
    generatedType,
    generatedId,
    emailSent,
    note }) => {

    let newMsg
    newMsg = state.messages.filter((message) => message.id === id)
    if (generated) {
      newMsg[0]['generated'] = generated
      newMsg[0]['generatedType'] = generatedType
      newMsg[0]['generatedId'] = generatedId
      newMsg[0]['value'] = value
      newMsg[0]['emailSent'] = emailSent
      newMsg[0]['gtMsg'] = gtMsg
      newMsg[0].error = null
    } else {
      newMsg[0]['value'] = value
      newMsg[0]['emailSent'] = emailSent
    }
    for (let i = 0; i < state.messages.length; i++) {
      if (state.messages[i].id === id) {
        state.messages[i] = newMsg[0];
        break;
      }
    }
  },
  REMOVE_MESSAGE: (state, id) => {
    state.messages = state.messages.filter(message => message.id !== id);
  },
  MESSAGE_UPDATED: (state, payload) => {
    let updatedMsg = state.messages.filter(msg => msg.id === payload.id)
    updatedMsg[0].updated = true
    updatedMsg[0].data = payload.data
    updatedMsg[0].error = null
    updatedMsg[0].value = `Successfully updated ${updatedMsg[0].resource}!`

    let indexToUpdate = state.messages.findIndex(obj => obj.id === payload.id);

    if (indexToUpdate !== -1) {
      state.messages.splice(indexToUpdate, 1, updatedMsg[0]);
    }
  },
  MESSAGE_UPDATE_FAILED: (state, payload) => {
    let updatedMsg = state.messages.filter(msg => msg.id === payload.id)
    updatedMsg[0].updated = false
    updatedMsg[0].error = payload.data

    let indexToUpdate = state.messages.findIndex(obj => obj.id === payload.id);

    if (indexToUpdate !== -1) {
      state.messages.splice(indexToUpdate, 1, updatedMsg[0]);
    }
  },

  CLEAR_MESSAGES: (state) => {
    state.messages = []
    state.chatTitle = 'All Open Opportunities'
  }

}

const actions = {
  async updateStages({ state, commit }) {
    if (!state.token) return null

    const res = await Status.api.list({})

    commit('UPDATE_STAGES', res.results ? res.results : null)
  },
  updateChatTitle({ commit }, title) {
    commit('UPDATE_CHAT_TITLE', title)
  },
  updateTask({ commit }, task) {
    commit('UPDATE_TASK', task)
  },
  setProcessedMeeting({ commit }, meetingName) {
    commit('UPDATE_MEETING_NAME', meetingName)
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
  async getSearches({ commit }) {
    try {
      await Comms.api.getSearches().then((response) => {
        commit('SAVE_SEARCHES', response.results)
      })
    } catch (e) {
      console.log(e)
    }
  },
  async getPitches({ commit }) {
    try {
      const response = await Comms.api.getPitches()
      commit('SAVE_PITCHES', response.results)
    } catch (e) {
      console.log(e)
    }
  },
  setSearch({ commit }, search) {
    commit('SET_SEARCH', search)
  },
  setPitch({ commit }, pitch) {
    commit('SET_PITCH', pitch)
  },
  setCurrentView({ commit }, view) {
    commit('SET_VIEW', view)
  },
  setCurrentMeeting({ commit }, meeting) {
    commit('SET_MEETING', meeting)
  },
  setCurrentOpp({ commit }, opp) {
    commit('SET_OPP', opp)
  },
  editMeeting({ commit }, { id, updated }) {
    commit('EDIT_MEETING', { id, updated })
  },
  editMessages({ commit }, {
    id,
    value,
    gtMsg,
    generated,
    generatedType,
    generatedId,
    emailSent,
    note }) {
    commit('EDIT_MESSAGES', {

      id,
      value,
      gtMsg,
      generated,
      generatedType,
      generatedId,
      emailSent,
      note
    })
  },
  setMeetingData({ commit }, { id, data }) {
    commit('SET_MEETING_DATA', { id, data })
  },
  removeMessage({ commit }, id) {
    commit('REMOVE_MESSAGE', id)
  },
  updateMessages({ commit }, message) {
    commit('UPDATE_MESSAGES', message)
  },
  messageUpdated({ commit }, { id, data }) {
    commit('MESSAGE_UPDATED', { id, data })
  },
  messageUpdateFailed({ commit }, { id, data }) {
    commit('MESSAGE_UPDATE_FAILED', { id, data })
  },
  clearMessages({ commit }) {
    commit('CLEAR_MESSAGES',)
  },
  changeFilters({ commit }, filters) {
    commit('UPDATE_FILTERS', filters)
  },
  async loadMoreChatOpps({ state, commit }, { page = 1, text }) {
    let resourceName = ''
    // const decryptedUser = decryptData(state.user, process.env.VUE_APP_SECRET_KEY)
    const decryptedUser = state.user
    if (decryptedUser.crm === 'SALESFORCE') {
      resourceName = 'Opportunity'
    } else if (decryptedUser.crm === 'HUBSPOT') {
      resourceName = 'Deal'
    }
    let oldResults = []
    if (page > 1) {
      oldResults = state.chatOpps.results
    }
    let res = await CRMObjects.api.getObjects(resourceName, page, true, [['CONTAINS', state.user.crm === 'SALESFORCE' ? 'Name' : 'dealname', text]])
    res.results = [...oldResults, ...res.results]
    commit('SAVE_CHAT_OPPS', res)
    return res
  },
  async loadChatOpps({ state, commit }, page = 1) {
    let resourceName = ''
    // const decryptedUser = decryptData(state.user, process.env.VUE_APP_SECRET_KEY)
    const decryptedUser = state.user
    if (decryptedUser.crm === 'SALESFORCE') {
      resourceName = 'Opportunity'
    } else if (decryptedUser.crm === 'HUBSPOT') {
      resourceName = 'Deal'
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
      const decryptedUser = state.user
      // const decryptedUser = decryptData(state.user, process.env.VUE_APP_SECRET_KEY)
      if (decryptedUser.crm === 'SALESFORCE') {
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
      // const decryptedUser = decryptData(state.user, process.env.VUE_APP_SECRET_KEY)
      const decryptedUser = state.user
      if (decryptedUser.crm === 'SALESFORCE') {
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
  async loadAllLeads({ state, commit }, filters = []) {
    // const decryptedUser = decryptData(state.user, process.env.VUE_APP_SECRET_KEY)
    const decryptedUser = state.user
    if (decryptedUser.crm === 'SALESFORCE') {
      try {
        const res = await CRMObjects.api.getObjectsForWorkflows('Lead', true, filters)
        commit('SAVE_ALL_LEADS', res.results)
      } catch (e) {
        console.log(e)
      }
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
  updateTempRefreshUser({ commit }, payload) {
    commit('UPDATE_TEMP_REFRESH_USER', payload)
  },
  updateGoogleSignIn({ commit }, payload) {
    commit('UPDATE_GOOGLE_SIGN_IN', payload)
  },
  updateSelectedArticle({ commit }, payload) {
    commit('UPDATE_SELECTED_ARTICLE', payload)
  },
  updateUserToken({ commit }, payload) {
    commit('UPDATE_USERTOKEN', payload)
  },
  async logoutUser({ state, commit }) {
    commit('LOGOUT_USER')
    await User.api.logout()
  },
  async refreshCurrentUser({ state, dispatch, commit }) {
    if (!state.token) {
      return null
    }
    // const decryptedUser = decryptData(state.user, process.env.VUE_APP_SECRET_KEY)
    const decryptedUser = state.user
    try {
      const user = await User.api.getUser(decryptedUser.id)
      // const encrypted = encryptData(user, process.env.VUE_APP_SECRET_KEY)
      // commit('UPDATE_USER', encrypted)
      commit('UPDATE_USER', user)
    } catch(e) {
      console.log('e refreshUser', e.response)
      // if (e.response.status === 401 && e.response.data.detail === 'Token expired') {
        // Handle the 401 Unauthorized error here
        // For example, you can log the user out or show an error message
        // You can also redirect the user to the login page
        // let tempUser
        // if (state.user && state.user.id) {
        //   store.dispatch('updateTempRefreshUser', state.user)
        //   tempUser = state.user
        // } else {
        //   tempUser = state.tempRefreshUser
        // }
        // const user = state.user
        // const token = state.token
        // // call refresh token endpoint
        // User.api.refreshToken(token, user && user.id ? user.id : tempUser.id).then((res) => {
        //   // with token, insert into store
        //   dispatch('updateUserToken', res.token).then(() => {
        //     // refresh user
        //     dispatch('updateTempRefreshUser', null)
        //     dispatch('refreshCurrentUser')
        //   })
        // })
      // }
      // do nothing for now
      return null
    }
  },
}

const plugins = [
  createPersistedState({
    key: STORAGE_KEY,
    storage: window.sessionStorage
  }),
]

const getters = {
  userIsLoggedIn: state => {
    let decryptedUser
    // let decryptedKey
    if (state.user) {
      // decryptedUser = decryptData(state.user, process.env.VUE_APP_SECRET_KEY)
    }
    if (state.token) {
      // decryptedKey = decryptData(state.token, process.env.VUE_APP_SECRET_KEY)
    }
    // return !!(decryptedKey && decryptedUser)
    return !!(state.user && state.token)
  },
  user: state => {
    return state.user
  },
  token: state => {
    return state.token
  },
  tempRefreshUser: state => {
    return state.tempRefreshUser
  }
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  plugins: [
    createPersistedState({
      paths: ['user', 'token',]
    })
  ],
})
