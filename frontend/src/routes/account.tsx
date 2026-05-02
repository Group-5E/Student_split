import { createFileRoute } from '@tanstack/react-router'
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import { Card, CardContent, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useState } from 'react'
import { useUser } from '@/hooks/useUser'
import { Button } from '@/components/ui/button'
import { Field, FieldLabel } from '@/components/ui/field'

export const Route = createFileRoute('/account')({
  component: RouteComponent,
})

function RouteComponent() {
  const { user } = useUser();
  const [username, setUserName] = useState(user.username);
  const [edit, setEdit] = useState(true)
  return (
    <div className="w-full h-full flex flex-wrap justify-center gap-2 p-5">
      <Card className='flex w-[40%]'>
        <CardTitle>
          <Avatar className="mx-auto size-50">
            <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
            <AvatarFallback>CN</AvatarFallback>
          </Avatar>
        </CardTitle>
        <CardContent>
          <form className='flex flex-col justify-start'>
            <Field>
              <FieldLabel htmlFor="username">username</FieldLabel>
              <Input
                id='username'
                type='username'
                value={username}
                readOnly={edit}
                onChange={(e) =>
                  setUserName(e.target.value)
                }
              />
              <Button
                variant="outline"
                type="button"
                onClick={(e) => {
                  e.preventDefault()
                  setEdit(!edit)
                }}
              >
                edit
              </Button>
            </Field>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
