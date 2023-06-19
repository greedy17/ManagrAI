<template>
  <section>
    {{ meetings }}
  </section>
</template>

<script>
export default {
  name: 'ChatMeetings',
  components: {},
  props: {},
  data() {
    return {}
  },
  methods: {},
  computed: {
    user() {
      return this.$store.state.user
    },
    meetings() {
      return this.$store.state.meetings
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
</style>