<template>
  <div>
    <div class="row" v-if="!isExpanded">
      <img
        v-if="!isExpanded"
        alt="icon"
        :src="require(`@/assets/images/more_horizontal.svg`)"
        class="icon"
        @click="isExpanded = !isExpanded"
      />
      <div class="thread-message-subject-unexpanded">
        <h3>{{ message.subject }}</h3>
      </div>
      <div class="thread-message-snippet-unexpanded">
        <span>
          {{ message.snippet }}
        </span>
      </div>
      <div class="thread-emails-unexpanded">
        <span class="thread-message-email">{{ message.to[0].name }}</span>
        <span class="thread-message-email">{{ message.from[0].name }}</span>
      </div>
    </div>
    <div v-if="isExpanded">
      <div class="row">
        <img
          v-if="isExpanded"
          alt="icon"
          :src="require(`@/assets/images/dropdown-arrow.svg`)"
          class="icon"
          @click="isExpanded = !isExpanded"
        />
        <div class="thread-message-subject-expanded">
          <h3>{{ message.subject }}</h3>
        </div>
        <div class="thread-emails-expanded">
          <span class="thread-message-email">To: {{ message.to[0].name }}</span>
          <span class="thread-message-email">From: {{ message.from[0].name }}</span>
        </div>
      </div>
      <div class="thread-body">
        <div v-html="message.body" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'message',
  props: {
    message: {
      type: Object,
      required: true,
    },
    isExpanded: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.thread-message {
  padding: 10px 15px;
  background-color: $silver;
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.9rem;
  @include base-font-styles();
  margin-bottom: 0.625rem;
}

.thread-message-icon {
  width: 10%;
}

.thread-message-subject-unexpanded {
  padding: 0 5px;
  width: 25%;
}

.thread-message-snippet-unexpanded {
  width: 50%;
}
.thread-message-emails-unexpanded {
  padding: 0 5px;
  width: 35%;
}

.thread-message-email {
  display: inline-block;
  font-size: 0.8rem;
  border: 1px solid $dark-gray-blue;
  padding: 5px 7px;
  margin: 2px 5px;
}
.row {
  display: flex;
  align-items: center;
}
</style>
