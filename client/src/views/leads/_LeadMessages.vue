<template>
  <div class="lead-messages"></div>
</template>

<script>
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
import LeadMessage from '@/services/lead-messages'
import CollectionManager from '@/services/collectionManager'

export default {
  name: 'LeadMessages',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  components: {
    ComponentLoadingSVG,
  },
  data() {
    return {
      leadMessages: CollectionManager.create({
        ModelClass: LeadMessage,
        filters: {},
      }),
    }
  },
  created() {
    this.leadMessages.refresh()
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';

.primary-button {
  @include primary-button;
}
</style>
