<template>
  <PopularWorkflows :closeBuilder="closeBuilder" :noRenderHeader="noRenderHeader" :config="userCRM === 'HUBSPOT' ? allConfigs.DEAL_REVIEW_HUBSPOT : allConfigs.DEAL_REVIEW" />
</template>

<script>
/**
 * Components
 * */
//Internal
import PopularWorkflows from '@/views/settings/alerts/create/templates/PopularWorkflows'
import allConfigs from '../../configs'

export default {
  name: 'DealReview',
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
    }
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
}
</script>
