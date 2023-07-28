<template>
  <PopularWorkflows
    @refresh-configs="refreshConfigs"
    :closePopularModal="closePopularModal"
    :config="config"
    :largeOpps="true"
    :selectField="true"
    :noRenderHeader="noRenderHeader"
    :closeBuilder="closeBuilder"
    :canSave="canSave"
    :saveWorkflow="saveWorkflow"
  />
</template>

<script>
/**
 * Components
 * */
//Internal
import PopularWorkflows from '@/views/settings/alerts/create/templates/PopularWorkflows'
import allConfigs from '../../configs'
import { decryptData } from '../../../../../encryption'

export default {
  name: 'LargeOpportunities',
  props: {
    noRenderHeader: {
      type: Boolean,
    },
    closeBuilder: {
      type: Function,
    },
    canSave: {
      type: Function,
    },
    saveWorkflow: {
      type: Function,
    },
    config: {
      type: Object,
    },
    closePopularModal: {
      type: Function,
    },
  },
  components: {
    PopularWorkflows,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      allConfigs,
    }
  },
  methods: {
    refreshConfigs() {
      this.$emit('refresh-configs')
    },
  },
  computed: {
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
  },
}
</script>