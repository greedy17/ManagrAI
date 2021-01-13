<template>
  <div class="integrations">
    <h2>Integrations</h2>

    <div class="integrations__cards">
      <div class="card">
        <img class="card-img" src="@/assets/images/salesforce.svg" />
        <h3>Salesforce</h3>
        <p class="card-text">Connect Salesforce to sync your Salesforce data with Managr.</p>
        <button class="primary-button">Connect</button>
      </div>

      <div class="card">
        <img class="card-img" src="@/assets/images/zoom_logo.svg" />
        <h3>Zoom</h3>
        <p class="card-text">
          Connect Zoom so Managr can help you track how your meetings went and send that info
          straight to Salesforce.
        </p>
        <button class="primary-button">Connect</button>
      </div>

      <div class="card">
        <img class="card-img" src="@/assets/images/slack.svg" />
        <h3>Slack</h3>
        <p class="card-text">
          Connect Slack to easily make updates to your Salesforce opportunities from within the
          Slack interface.
        </p>
        <button class="primary-button">Connect</button>
      </div>

      <div class="card">
        <img
          class="card-img"
          src="@/assets/images/google-calendar.svg"
          style="margin-right: 1rem"
        />
        <img class="card-img" src="@/assets/images/outlook-icon.svg" />
        <h3>Calendar</h3>
        <p class="card-text">
          Connect you calendar and Managr will make sure that you capture all the contacts who
          attended your meetings.
        </p>
        <button class="primary-button">Connect</button>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Page that shows a grid of all possible integrations and 'Connect' buttons.
 */
export default {
  name: 'Integrations',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.integrations {
  &__cards {
    display: flex;
    flex-wrap: wrap;
  }
}

.card {
  flex: 1;
  min-width: 28rem;
  max-width: 28rem;
  margin-right: 1rem;
  margin-bottom: 1rem;
}

.card-img {
  height: 4rem;
}

.card-text {
  font-size: 1.1rem;
  color: $light-gray-blue;
  min-height: 6rem;
}
</style>
