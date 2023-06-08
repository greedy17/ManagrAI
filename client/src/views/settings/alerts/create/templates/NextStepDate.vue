<template>
  <PopularWorkflows :closeBuilder="closeBuilder" :noRenderHeader="noRenderHeader" :selectField="true" :config="userCRM === 'HUBSPOT' ? allConfigs.UPCOMING_NEXT_STEP_HUBSPOT : allConfigs.UPCOMING_NEXT_STEP" />
</template>

<script>
/**
 * Components
 * */
//Internal
import PopularWorkflows from '@/views/settings/alerts/create/templates/PopularWorkflows'
import allConfigs from '../../configs'

export default {
  name: 'UpcomingNextStep',
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
