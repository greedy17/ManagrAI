<template>
  <PopularWorkflows
    :config="
      userCRM == 'HUBSPOT' ? allConfigs.CLOSING_NEXT_MONTH_HUBSPOT : allConfigs.CLOSING_NEXT_MONTH
    "
    :noRenderHeader="noRenderHeader"
    :closeBuilder="closeBuilder"
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
  name: 'ClosingNextMonth',
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
