<template>
  <div class="thread">
    <div class="row" v-if="!isExpanded">
      <img
        v-if="!isExpanded"
        alt="icon"
        :src="require(`@/assets/images/more_horizontal.svg`)"
        class="icon"
        @click="isExpanded = !isExpanded"
      />
      <div class="thread-subject-unexpanded">
        <h3>{{ thread.subject }}</h3>
      </div>
      <div class="thread-snippet-unexpanded">
        <span>
          {{ thread.snippet }}
        </span>
      </div>
      <div class="thread-emails-unexpanded">
        <span
          v-for="(participant, index) in thread.participants"
          :key="index"
          v-if="participant.name.length > 0"
          class="thread-email"
        >
          {{ participant.name }}
        </span>
      </div>
    </div>
    <div v-if="isExpanded">
      <div class="row">
        <img
          alt="icon"
          :src="require(`@/assets/images/dropdown-arrow.svg`)"
          class="icon"
          @click="isExpanded = !isExpanded"
        />
      </div>
      <div class="row" v-for="(message, index) in messages" :key="message.id">
        <ThreadMessage
          :message="message"
          :is-expanded="true"
          style="margin-left: 25px"
          v-if="index === 0"
        ></ThreadMessage>
        <ThreadMessage
          :message="message"
          style="margin-left: 25px"
          v-if="index > 0"
        ></ThreadMessage>
      </div>
    </div>
  </div>
</template>

<script>
import ThreadMessage from '@/components/emails/ThreadMessage'
import Nylas from '@/services/nylas'

export default {
  name: 'Thread',
  components: { ThreadMessage },
  props: {
    thread: {
      type: Object,
      required: true,
    },
    isExpanded: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      messages: {},
    }
  },
  created() {
    Nylas.getThreadMessages(this.thread.id).then(response => {
      this.messages = response.data
    })
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.thread {
  padding: 10px 15px;
  background-color: $silver;
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.9rem;
  @include base-font-styles();
  margin-bottom: 0.625rem;
}

.thread-icon {
  width: 10%;
}

.thread-subject-unexpanded {
  padding: 0 5px;
  width: 25%;
}

.thread-snippet-unexpanded {
  width: 50%;
}
.thread-emails-unexpanded {
  padding: 0 5px;
  width: 35%;
}

.thread-email {
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
