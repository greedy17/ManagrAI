<template>
  <div class="toolbar">
    <div class="top-menu">
      <img class="edit icon" src="@/assets/images/pencil.svg" alt="icon" />
      <img class="more icon" src="@/assets/images/more_horizontal.svg" alt="icon" />
    </div>
    <div class="lead-name">
      <h2>{{ lead.name }}</h2>
    </div>
    <div class="rating">
      <LeadRating :label="true" :rating="lead.rating" />
    </div>
    <div class="lead-lists">
      <div class="header">Lists</div>
      <div class="container">
        <LeadList
          class="list"
          v-for="list in lead.lists"
          :key="list.id"
          :listName="list.title"
          :dark="true"
        />
      </div>
    </div>
    <!--- focus --- -->
    <div class="account-link">Account</div>
    <div class="amount section-shadow">Amount: {{ lead.amount | currency }}</div>
    <!--- focus --- -->
    <div class="contacts">
      <div class="header section-shadow">
        <span>Contacts</span>
      </div>
      <div class="contacts-container">
        <div class="contact section-shadow" v-for="contact in exampleContacts" :key="contact.id">
          <img src="@/assets/images/sara-smith.png" alt="contact image" />
          <span class="name">{{ contact.name }}</span>
          <div class="phone button">
            <img class="icon" src="@/assets/images/telephone.svg" alt="icon" />
          </div>
          <div class="email button">
            <img class="icon" src="@/assets/images/email.svg" alt="icon" />
          </div>
        </div>
      </div>
    </div>
    <div class="files">
      <div class="header section-shadow">
        <span>Files</span>
      </div>
      <div class="files-container">
        <div class="file section-shadow" v-for="file in exampleFiles" :key="file">
          <img class="icon" src="@/assets/images/document.svg" alt="icon" />
          {{ file }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LeadRating from '@/components/shared/LeadRating'
import LeadList from '@/components/shared/LeadList'

const exampleFiles = ['Filename.pdf', 'filename2.pdf', 'filename3.jpeg']
const exampleContacts = [
  { id: 1, name: 'Sara Smith' },
  { id: 2, name: 'Jake Murray' },
]

export default {
  name: 'ToolBar',
  components: {
    LeadRating,
    LeadList,
  },
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return { exampleFiles, exampleContacts }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.toolbar {
  @include standard-border();
  background-color: $white;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  height: 50rem;
  width: 100%;
  display: flex;
  flex-flow: column;
}

.toolbar,
.toolbar > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 14px;
}

.top-menu {
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 2.125rem;
  padding: 0 0.75rem;

  .icon {
    height: 1.25rem;
    opacity: 0.4;
  }

  .edit {
    margin-right: auto;
  }

  .more {
    margin-left: auto;
  }
}

.lead-name {
  padding: 0 15%;
  text-align: center;
}

.rating {
  display: flex;
  flex-flow: row;
  justify-content: center;
}

.lead-lists {
  padding: 1.25rem 1.25rem 0.625rem 1.25rem;
  border-bottom: 5px solid $coral;

  .header {
    margin-bottom: 0.625rem;
  }

  .container {
    display: flex;
    flex-flow: column;

    .list {
      margin-bottom: 0.625rem;
      height: 1.75rem;
    }
  }
}

.account-link {
  height: 3rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;

  color: $dark-green;
  text-decoration: underline;
}

.amount {
  height: 3rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;

  font-size: 18px;
}

.contacts {
  .header {
    padding-left: 1.25rem;
    height: 3.375rem;
    display: flex;
    flex-flow: row;
    align-items: center;

    span {
      font-weight: bold;
    }
  }
  .contact {
    display: flex;
    flex-flow: row;
    align-items: center;
    height: 3rem;
    padding-left: 1.25rem;
    font-size: 14px;

    img {
      height: 1.25rem;
      border-radius: 50%;
      margin-right: 1rem;
    }

    .phone {
      margin-left: auto;
    }

    .email {
      margin: 0 0.625rem;
    }

    .button {
      @include pointer-on-hover();
      height: 1.875rem;
      width: 1.875rem;
      background-color: $soft-gray;
      border-radius: 5px;
      display: flex;
      flex-flow: row;
      align-items: center;
      justify-content: center;

      .icon {
        height: 1rem;
        margin: auto;
      }

      .email {
        margin-left: 0.625rem;
      }

      .phone {
        margin-left: auto;
      }
    }
  }
}

.files {
  .header {
    padding-left: 1.25rem;
    height: 3.375rem;
    display: flex;
    flex-flow: row;
    align-items: center;

    span {
      font-weight: bold;
    }
  }
  .file {
    display: flex;
    flex-flow: row;
    align-items: center;
    height: 3rem;
    padding-left: 1.25rem;
    font-size: 14px;

    .icon {
      height: 1.25rem;
      opacity: 0.6;
      margin-right: 1rem;
    }
  }
}
</style>
