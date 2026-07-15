<template>
  <AppLayout>
    <PageHeader
      eyebrow="Company workspace"
      title="Selected students"
      subtitle="Manage joining details and offer packages."
      back-to="/company/dashboard"
      back-label="Dashboard"
    />

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />

    <StateMessage
      v-else-if="selected.length === 0"
      icon="fas fa-user-check"
      title="No selected students yet"
      description="Students you mark as Selected in Applications will appear here."
    />

    <template v-else>
      <div class="row g-4">
        <div v-for="item in selected" :key="item.id" class="col-12 col-md-6 col-lg-4">
          <div class="pp-panel py-3 h-100">
            <div class="d-flex justify-content-between gap-3 mb-2">
              <div class="d-flex align-items-center gap-2">
                <EntityAvatar :name="item.student_name" :size="36" />
                <div>
                  <h2 class="h6 fw-bold mb-0" style="color: var(--pp-navy)">
                    {{ item.student_name }}
                  </h2>
                  <div class="small text-muted">{{ item.job_title }}</div>
                </div>
              </div>
              <span class="badge-status badge-green"
                ><i class="fas fa-check-circle" aria-hidden="true"></i>Selected</span
              >
            </div>
            <div class="small text-muted mb-3">
              <div>
                <i class="fas fa-calendar-check me-1" aria-hidden="true"></i>Join date:
                {{ formatDate(item.join_date) }}
              </div>
              <div>
                <i class="fas fa-rupee-sign me-1" aria-hidden="true"></i>Package:
                {{ item.package_lpa ? `${item.package_lpa} LPA` : "N/A" }}
              </div>
            </div>
            <div class="mt-2">
              <button
                class="btn-pp-outline btn-sm w-100"
                type="button"
                @click="viewPlacement(item.id)"
              >
                <i class="fas fa-eye me-1" aria-hidden="true"></i>View
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppLayout from "../layouts/AppLayout.vue";
import PageHeader from "../components/PageHeader.vue";
import EntityAvatar from "../components/EntityAvatar.vue";
import StateMessage from "../components/StateMessage.vue";
import SkeletonBlock from "../components/SkeletonBlock.vue";
import http from "../api/http";
import { useToast } from "../composables/useToast";

const toast = useToast();
const loading = ref(true);
const selected = ref([]);
const router = useRouter();

onMounted(async () => {
  loading.value = true;
  try {
    const response = await http.get("/api/v1/company/selected-students");
    selected.value = response.data.selected || [];
  } finally {
    loading.value = false;
  }
});

function viewPlacement(id) {
  router.push(`/company/selected-students/${id}`);
}

function formatDate(value) {
  return value
    ? new Date(value).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : "N/A";
}
</script>
