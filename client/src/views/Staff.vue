<template>
  <div class="pipelines">
    <div class="pipelines__center">
      </div>
      <div :key="i" v-for="(org, i) in organizations.list">
        <h1>{{ org.name }}</h1>  
        <div class="form__list">
            <div class="form__list_item" :key="i" v-for="(form, i) in allForms">
                <div v-if="org.id === form.organization">
                    <h3>{{form.formType}} {{form.resource}}</h3>
                    <p>Form Fields:</p>
                    <ul>
                        <li class="field__list_item" :key="i" v-for="(field, i) in form.fieldsRef"><span>{{field.order}}-{{field.label}}</span><span class="sub_text">{{field.dataType}}</span></li>
                    </ul>
                </div>
            </div>
        </div>

      </div>
      
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'
import CollectionManager from '@/services/collectionManager'
import Organization from '@/services/organizations'

export default {
  name: 'Staff',
  data() {
    return {
      allForms: null,
      organizations: CollectionManager.create({ ModelClass: Organization }),
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  methods: {
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.allForms = res
        console.log(this.allForms)
      } catch (e) {
        console.log(e)
      }
    },
  },
  created() {
    this.getAllForms()
    this.organizations.refresh()
    console.log(this.organizations)
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.pipelines {
  margin-top: 3rem;
  color: $base-gray;

  &__preview {
    display: flex;
    align-items: flex-start;
    flex-direction: column;
    margin: 1rem 3rem;
    z-index: 2;
  }
  &__center {
    display: flex;
    align-items: flex-start;
    justify-content: space-evenly;
  }
}

.preview-border {
  box-shadow: 4px 5px 9px $very-light-gray;
  background-color: white;
  margin-top: 2rem;
  border-radius: 0.5rem;
  width: 51vw;
}
.spacer {
  height: 20vh;
}
p {
  font-size: 14px;
}
h1 {
  margin-top: -1px;
  margin-left: -0.1rem;
  font-size: 38px;
}
.form__list {
  display: flex;
  flex-wrap: wrap;
}
.form__list_item {
  padding: 3rem;
  border: 1px solid black;
}
.sub_text {
  font-size: 12px;
  padding-left: 1rem;
}

.field__list_item {
  display: flex;
  flex-direction: column;
}
</style>