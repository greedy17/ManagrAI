<template>
  <div class="integrations">
    <h2>Integrations</h2>

    <div class="integrations__cards">
      <div class="card">
        <img class="card-img" src="@/assets/images/salesforce.svg" />
        <h3>Salesforce</h3>
        <p class="card-text">
          Connect Salesforce to sync Accounts, Opportunities & Contacts with managr.
        </p>
        <button class="primary-button">Connect</button>
      </div>

      <div class="card">
        <img class="card-img" src="@/assets/images/zoom_logo.svg" />
        <h3>Zoom</h3>
        <p class="card-text">
          Connect Zoom to sync meeting data with managr.
        </p>
        <button class="primary-button">Connect</button>
      </div>

      <div class="card">
        <img class="card-img" src="@/assets/images/slack.svg" />
        <h3>Slack</h3>
        <p class="card-text">
          Connect Slack to enable messaging between apps.
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
          Connect Calendar to access upcoming meetings & attendees.
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
  margin-right: 2rem;
  margin-bottom: 2rem;
}

.card-img {
  height: 4rem;
}

.card-text {
  font-size: 1.1rem;
  color: $light-gray-blue;
  min-height: 4rem;
}
</style>
