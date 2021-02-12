<script>
import FormSettings from './_FormSettings'
import { mapState } from 'vuex'
import SlackOAuth, { salesforceFields } from '@/services/slack'
export default {
  extends: FormSettings,
  name: 'FormSettings',
  components: {},
  data() {
    return {
      isLoading: false,
    }
  },
  async created() {
    console.log('acc')
    try {
      this.forms = await SlackOAuth.api.getOrgCustomForm('Account')
    } catch (error) {
      console.log(error)
    }
    this.toggleSelectedTab('MEETING_REVIEW')
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
</style>
