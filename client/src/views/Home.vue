<template>
  <div class="home">
    <div class="heading">
      <h3>Hi {{ user.firstName }}</h3>
      <p>Today is Tuesday, August 23, 2022</p>
    </div>

    <section class="command-center">
      <div class="command-center__section">
        <p>
          Meetings <span>{{ meetings.length }}</span>
        </p>
        <section>
          <Meetings />
        </section>
      </div>

      <div class="command-center__section-pipeline">
        <p>
          Pipeline <span>{{ templates.list ? templates.list.length : 0 }}</span>
        </p>
        <section>
          <PipelineOverview />
        </section>
      </div>

      <div>
        <p>Activity</p>
        <div class="column-section-small neg-margin">
          <!-- <img src="@/assets/images/settings.svg" height="20px" alt="" /> -->
          <section>
            <ForecastOverview />
          </section>
        </div>
        <div class="column-section">
          <!-- <img src="@/assets/images/settings.svg" height="20px" alt="" /> -->
          <section></section>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import Meetings from '@/views/Meetings'
import PipelineOverview from '@/components/PipelineOverview'
import ForecastOverview from '@/components/ForecastOverview'
import { CollectionManager } from '@thinknimble/tn-models'
import AlertTemplate from '@/services/alerts/'

export default {
  name: 'Home',
  components: {
    Meetings,
    PipelineOverview,
    ForecastOverview,
  },
  data() {
    return {
      user: this.$store.state.user,
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
    }
  },
  async created() {
    this.templates.refresh()
  },
  computed: {
    meetings() {
      return this.$store.state.meetings
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.home {
  margin-left: 80px;
  letter-spacing: 0.75px;
}
.heading {
  h3 {
    margin-bottom: 0;
    font-size: 24px;
  }
  p {
    font-size: 13px;
    color: $light-gray-blue;
  }
}

.command-center {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;

  &__section {
    width: 25vw;
    p {
      font-size: 14px;
      font-weight: bold;
      margin-left: 2px;

      span {
        background-color: $light-coral;
        color: $coral;
        border-radius: 6px;
        padding: 2px 8px;
        margin-left: 8px;
        font-size: 12px;
      }
    }
  }

  &__section-pipeline {
    width: 40vw;

    p {
      font-size: 14px;
      span {
        background-color: $base-gray;
        color: white;
        padding: 2px 8px;
        border-radius: 6px;
        margin-left: 4px;
        font-size: 11px;
      }

      div {
        img {
          margin-left: 12px;
        }
      }
    }
  }

  section {
    width: 100%;
    // box-shadow: 1px 1px 2px 1px $very-light-gray;
    border: 1px solid $soft-gray;
    height: 100%;
    margin-top: 8px;
    height: 70vh;
    border-radius: 8px;
    overflow-y: scroll;
    background-color: white;
  }
}
.column-section {
  display: flex;
  flex-direction: column;
  align-items: center;

  section {
    border: 1px solid $soft-gray;
    width: 22vw;
    height: 45vh;
  }
}
.column-section-small {
  display: flex;
  flex-direction: column;
  align-items: center;

  section {
    border: 1px solid $soft-gray;
    width: 22vw;
    height: 24vh;
  }
}
.neg-margin {
  margin-top: -12px;
}
</style>