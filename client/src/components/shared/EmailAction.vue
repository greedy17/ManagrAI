<template>
  <div class="box__content">
    <template v-if="!isTextConnected">
      <div>
        <span class="muted">
          <span class="muted">
            Please Enable Email Integration to use this feature in your settings
          </span>
        </span>
      </div>
    </template>
    <EmailCompose v-else :lead="lead" />
  </div>
</template>

<script>
import EmailCompose from '@/components/emails/EmailCompose'

export default {
  name: 'EmailAction',
  components: { EmailCompose },
  computed: {
    isTextConnected() {
      return !!this.$store.state.user.textConnected
    },
  },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/emails';
</style>
