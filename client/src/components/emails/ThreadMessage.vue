<template>
  <div class="actions__item">
    <div @click="isExpanded = !isExpanded" style="cursor: pointer;">
      <!-- Message Preview -->
      <div class="actions__row">
        <div class="actions__item-header-icon" style="flex: 0; margin-right: 0.5rem;">
          <img
            alt="icon"
            :src="require(`@/assets/images/email.svg`)"
            :class="{ 'filter-green': isExpanded }"
            class="icon"
          />
        </div>

        <div class="actions__item-header-title" v-if="!isExpanded" style="margin-right: 1rem;">
          <span>
            {{ message.from.map(c => c.email).join(', ') }}
          </span>
        </div>

        <div class="actions__item-header-title">
          <span>
            {{ message.subject }}
          </span>
        </div>

        <div
          class="actions__item-header-date"
          style="display: flex; flex-direction: column; align-items: flex-end;"
        >
          <span :title="message.date | momentDateTimeShort" style="flex: 1; text-align: right;">
            {{ (message.date * 1000) | timeAgo }}
          </span>
        </div>
      </div>

      <div class="actions__row" v-if="!isExpanded">
        <div class="actions__item-header-date">
          to
          <div v-for="(contact, index) in message.to" class="email__contact-tag" :key="index">
            {{ contact.email }}
          </div>
        </div>
      </div>
      <!-- End Message Preview -->
    </div>

    <!-- Message expanded -->
    <div v-if="isExpanded">
      <div class="email__row">
        <strong v-for="(contact, index) in message.from" :key="index">
          {{ message.from.map(c => c.email).join(', ') }}
        </strong>
      </div>
      <div class="email__row">
        to
        <div v-for="(contact, index) in message.to" class="email__contact-tag" :key="index">
          {{ contact.email }}
        </div>
      </div>
    </div>

    <!-- Thread Message Body -->
    <div v-if="isExpanded">
      <div v-html="message.body"></div>
    </div>

    <!-- TODO: BREAK THIS OUT INTO ITS OWN COMPONENT-->
    <h5 class="is-title" v-if="message.files.length > 0">
      Attachments
    </h5>

    <div class="email__row">
      <!-- TODO: Change this to a file-specific style instead of using the contact-tag -->
      <span
        v-for="file in filesWithNames"
        class="email__contact-tag email__contact-tag--green"
        :key="file.id"
      >
        <a :href="`/api/get-file/${file.id}/`" target="_blank">
          {{ file.filename }}
        </a>
      </span>
    </div>

    <div style="width: 100%" v-if="isExpanded">
      <div class="box" v-if="isExpanded"></div>
      <EmailCompose
        :lead="lead"
        @emailSent="emailSent"
        :reply-message="message"
        :show-subject="false"
      ></EmailCompose>
    </div>
  </div>
</template>

<script>
import EmailCompose from '@/components/emails/EmailCompose'

export default {
  name: 'message',
  components: { EmailCompose },
  props: {
    message: {
      type: Object,
      required: true,
    },
    initiallyExpanded: {
      type: Boolean,
      required: false,
      default: false,
    },
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isExpanded: false,
    }
  },
  created() {
    this.isExpanded = this.initiallyExpanded
  },
  computed: {
    /**
     * Some files appear to come back from Nylas without names
     * and without any content. Just filter these out.
     */
    filesWithNames() {
      return this.message.files.filter(f => !!f.filename)
    },
  },
  methods: {
    emailSent() {
      this.$emit('emailSent')
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/mixins/utils';
.filter-green {
  filter: invert(45%) sepia(96%) saturate(2978%) hue-rotate(123deg) brightness(92%) contrast(80%);
}
</style>
