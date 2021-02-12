<script>
import FormSettings from './_FormSettings'
import { mapState } from 'vuex'

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
    this.resource = 'Opportunity'
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
