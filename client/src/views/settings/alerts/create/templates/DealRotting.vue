<template>
  <PopularWorkflows
    @refresh-configs="refreshConfigs"
    :closePopularModal="closePopularModal"
    :canSave="canSave"
    :saveWorkflow="saveWorkflow"
    :closeBuilder="closeBuilder"
    :noRenderHeader="noRenderHeader"
    :config="config"
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
  name: 'DealReview',
  components: {
    PopularWorkflows,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
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
