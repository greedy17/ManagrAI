<template>
  <div class="box__content">
    <EmailCompose :lead="lead" />
  </div>
</template>

<script>
import EmailCompose from '@/components/emails/EmailCompose'

export default {
  name: 'EmailAction',
  components: { EmailCompose },
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
