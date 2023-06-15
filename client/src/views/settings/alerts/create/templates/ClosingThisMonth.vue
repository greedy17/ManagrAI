<template>
  <PopularWorkflows
    :closePopularModal="closePopularModal"
    :config="config"
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

export default {
  name: 'ClosingThisMonth',
  components: {
    PopularWorkflows,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    noRenderHeader: {
      type: Boolean
    },
    closeBuilder: {
      type: Function
    },
    canSave: { 
      type: Function
    },
    saveWorkflow: { 
      type: Function 
    },
    config: {
      type: Object
    },
    closePopularModal: {
      type: Function
    },
  },
  data() {
    return {
      allConfigs,
    }
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
  },
  mounted() {
    console.log(this.allConfigs.CLOSING_THIS_MONTH)
  },
}
</script>
