<template>
  <div class="notification-settings">
    <div class="notification-settings--box">
      <div class="notification-settings--box__header notification-settings--box__title">
        Configure Notification Settings
      </div>
      <div class="notification-settings--box__content">
        <div :key="opt.meta.id" v-for="opt in fields" class="notification-settings__option">
          <span class="notification-settings__option__title"
            >Please turn
            <span class="notification-settings__option__title--strong">{{ opt.meta.type }}</span>
            notifications for {{ opt.field.name }}
            <span
              :class="{
                'notification-settings__option__title--on': opt.field.value == true,
                'notification-settings__option__title--off': opt.field.value == false,
              }"
              >{{ opt.field.value == true ? 'on' : 'off' }}</span
            >
            <svg width="20px" height="20px" viewBox="0 0 15 15">
              <use
                xlink:href="@/assets/images/help-outline.svg#help-outline"
                v-tooltip="opt.meta.helpText"
              />
            </svg>
          </span>
          <div class="notification-settings__option__options">
            <input
              type="radio"
              v-model="opt.field.value"
              :value="true"
              :name="opt.field.name + '-' + opt.meta.type"
            />
            On
            <input
              type="radio"
              v-model="opt.field.value"
              :value="false"
              :name="opt.field.name + '-' + opt.meta.type"
            />
            Off
          </div>
        </div>
      </div>
      <div class="notification-settings--box__footer">
        <button
          :disabled="loading"
          class="notification-settings__button--primary"
          @click="updateSettings"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { FormField } from '@thinknimble/tn-forms'

import NotificationSettings, { NotificationSelection } from '@/services/notifications/settings'
import CollectionManager from '@/services/collectionManager'

// since this is a dynamic form we will only use form fields to generate without a form class

export default {
  name: 'NotificationSettings',
  components: {},
  data() {
    return {
      settingsOptions: CollectionManager.create({
        ModelClass: NotificationSettings,
      }),
      fields: [],
      loading: false,
    }
  },

  async created() {
    this.loading = true
    try {
      await this.settingsOptions.refresh()
      this.generateSettingsForm()
    } finally {
      this.loading = false
    }
  },
  methods: {
    generateSettingsForm() {
      let fields = this.settingsOptions.list.map(opt => {
        return {
          field: new FormField({ name: opt.title, value: opt.value.value }),
          meta: {
            type: opt.notificationType,
            helpText: opt.description,
            id: opt.id,
            selection: opt.value.id,
          },
        }
      })
      this.fields = fields
    },
    generateSubmission() {
      return {
        selections: this.fields.map(field => {
          return new NotificationSelection({
            option: field.meta.id,
            value: field.field.value,
            id: field.meta.selection,
          })
        }),
      }
    },
    async updateSettings() {
      if (!this.loading) {
        this.loading
        let selections = this.generateSubmission()

        try {
          await NotificationSettings.api.updateSettings(selections)
          this.$Alert.alert({
            type: 'success',
            timeout: 3000,
            message: 'Settings Saved',
          })
        } finally {
          this.loading = false
        }
      }
    },
  },

  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers.scss';
@import '@/styles/mixins/buttons.scss';
.notification-settings {
  &--box {
    @include box--bordered();
  }
  &__button--primary {
    @include primary-button;
  }
  &__option {
    display: flex;
    flex-direction: column;
    &__title,
    &__options {
      padding: 1rem;
    }

    &__title {
      width: 80%;
      display: flex;
      justify-content: space-between;
      text-transform: capitalize;
      &--strong {
        font-style: italic;
      }
      &--off {
        font-weight: bold;
        color: red;
      }
      &--on {
        font-weight: bold;
        color: green;
      }
    }
  }
}
</style>
